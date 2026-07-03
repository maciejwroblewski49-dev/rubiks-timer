"""External hardware timer over the audio jack (MoYu / StackMat)."""
import math, threading, time

import queue as _queue
# sounddevice + PortAudio DLL takes ~200 ms to import; load it lazily and
# pre-warm from a background thread so the audio timer panel is instant when
# the user opens it, without blocking cold startup.
_sd = None
_MOYU_OK = None                     # None = not tried yet
_MOYU_LOAD_LOCK = threading.Lock()
def _load_sounddevice():
    global _sd, _MOYU_OK
    with _MOYU_LOAD_LOCK:
        if _MOYU_OK is not None:
            return _MOYU_OK
        try:
            import sounddevice as sd
            _sd = sd; _MOYU_OK = True
        except Exception:
            _sd = None; _MOYU_OK = False
    return _MOYU_OK


class _AudioTimerDecoder:
    """Port of csTimer's audio decoder.  mode 'm'=MoYu (24-bit BCD @8000),
    's'=StackMat (UART 1200).  Calls on_state(dict) with time_milli."""
    def __init__(self, sample_rate, mode, on_state):
        self.mode = mode
        self.spb = sample_rate / (8000.0 if mode == 'm' else 1200.0)
        self.agc = 0.001 / self.spb
        self.last_power = 1.0
        self.lastVal = [0.0] * max(1, math.ceil(self.spb / 6))
        self.lastSgn = 0; self.lenKeep = 0
        self.bitBuf = []; self.byteBuf = []
        self.idle_val = 0; self.last_bit = 0; self.last_bit_len = 0; self.no_state_len = 0
        self.state = {'on': False, 'time_milli': 0, 'running': False, 'signalHeader': 'I'}
        self.cb = on_state

    def feed(self, samples):
        for s in samples:
            s = float(s); p = s * s
            self.last_power = max(1e-4, self.last_power + (p - self.last_power) * self.agc)
            self._proc(s / math.sqrt(self.last_power))

    def _proc(self, sig):
        self.lastVal.insert(0, sig); popped = self.lastVal.pop()
        sgn = 1 if self.lastSgn else -1
        edge = ((popped - sig) * sgn > 0.7 and abs(sig - sgn) - 1 > 0.2 and self.lenKeep > self.spb * 0.6)
        analyzer = self._moyu if self.mode == 'm' else self._stk
        if edge:
            for _ in range(round(self.lenKeep / self.spb)):
                analyzer(self.lastSgn)
            self.lastSgn ^= 1; self.lenKeep = 0
        elif self.lenKeep > self.spb * 2:
            analyzer(self.lastSgn); self.lenKeep -= self.spb
        self.lenKeep += 1

    def _moyu(self, bit):
        if self.last_bit != self.idle_val and self.last_bit_len == 1:
            self.bitBuf.append(bit)
            if len(self.bitBuf) == 24:
                t = 0
                for i in range(5, -1, -1):
                    t *= 10
                    for j in range(4):
                        t += self.bitBuf[i*4 + j] << j
                self.bitBuf = []; self._push('S', t)
        if bit != self.last_bit:
            self.last_bit = bit; self.last_bit_len = 1
        else:
            self.last_bit_len += 1
        if self.last_bit_len > 10:
            self.idle_val = bit; self.bitBuf = []; self.byteBuf = []
            if self.last_bit_len > 1000 and self.state['on']:
                self.state['on'] = False; self.cb(dict(self.state))
            elif self.last_bit_len > 4000:
                self.last_bit_len = 1000; self.cb(dict(self.state))

    def _stk(self, bit):
        self.bitBuf.append(bit)
        if bit != self.last_bit: self.last_bit = bit; self.last_bit_len = 1
        else: self.last_bit_len += 1
        self.no_state_len += 1
        if self.last_bit_len > 10:
            self.idle_val = bit; self.bitBuf = []
            if self.byteBuf: self.byteBuf = []
            if self.last_bit_len > 100 and self.state['on']:
                self.state['on'] = False; self.cb(dict(self.state))
            elif self.no_state_len > 700:
                self.no_state_len = 100; self.cb(dict(self.state))
        elif len(self.bitBuf) == 10:
            if self.bitBuf[0] == self.idle_val or self.bitBuf[9] != self.idle_val:
                self.bitBuf = self.bitBuf[1:]
            else:
                v = 0
                for i in range(8, 0, -1):
                    v = (v << 1) | (1 if self.bitBuf[i] == self.idle_val else 0)
                self.byteBuf.append(chr(v)); self._decode_stk(); self.bitBuf = []

    def _decode_stk(self):
        bb = self.byteBuf
        if len(bb) not in (9, 10): return
        if bb[0] not in ' SILRCA': return
        cs = 64
        for i in range(1, len(bb) - 3):
            if not bb[i].isdigit(): return
            cs += int(bb[i])
        if cs != ord(bb[-3]): return
        mm = int(bb[1]); ss = int(bb[2] + bb[3])
        ms = int(bb[4] + bb[5] + (bb[6] if len(bb) == 10 else '0'))
        self._push(bb[0], mm*60000 + ss*1000 + ms)

    def _push(self, head, t):
        prev = self.state['time_milli']
        self.state = {'on': True, 'time_milli': t, 'signalHeader': head,
                      'running': head == ' ' or t > prev}
        self.no_state_len = 0; self.cb(dict(self.state))


class MoyuInput:
    """Background audio capture + decode for an external timer (MoYu/StackMat)."""
    def __init__(self, mode='m'):
        self.mode = mode; self.stream = None; self.dec = None
        self.error = ""; self.device_name = ""
        self._latest = {'on': False, 'time_milli': 0}
        self._q = None; self._worker = None; self._stop_flag = False

    @staticmethod
    def available():
        return _load_sounddevice()

    @staticmethod
    def list_devices():
        out = []
        if not _load_sounddevice(): return out
        try:
            for i, d in enumerate(_sd.query_devices()):
                if d.get('max_input_channels', 0) > 0:
                    out.append((i, d['name']))
        except Exception:
            pass
        return out

    def start(self, device_name=""):
        self.stop()
        if not _load_sounddevice():
            self.error = "Brak biblioteki audio (sounddevice)"; return False
        try:
            idx = None
            for i, n in self.list_devices():
                if device_name and n == device_name:
                    idx = i; break
            if idx is None:
                devs = self.list_devices()
                if not devs:
                    self.error = "Brak wejść audio"; return False
                idx = devs[0][0]
            info = _sd.query_devices(idx)
            # Prefer 48000 Hz → exactly 6 samples per MoYu bit; 44100 gives 5.51,
            # whose rounding drift makes the pulse-width decode misread bits.
            # Audio buffer:
            #   • MoYu   → 'high' latency to ride out GIL stalls (no CRC, so a
            #     dropped sample = wrong reading);
            #   • StackMat → low latency; the CRC discards any bad packet, so
            #     a smaller buffer just means faster response with no risk.
            lat = 'high' if self.mode == 'm' else 'low'
            last_err = None
            for sr in (48000, int(info['default_samplerate']), 44100):
                try:
                    self.dec = _AudioTimerDecoder(sr, self.mode, self._on_state)
                    self.stream = _sd.InputStream(device=idx, channels=1, samplerate=sr,
                                                  blocksize=0, dtype='float32',
                                                  latency=lat, callback=self._cb)
                    self.stream.start()
                    self.device_name = "%s @ %dHz" % (info['name'], sr); self.error = ""
                    return True
                except Exception as e:
                    last_err = e; self.stream = None
            self.error = str(last_err); return False
        except Exception as e:
            self.error = str(e); self.stream = None; return False

    def _cb(self, indata, frames, t, status):
        try:
            self.dec.feed(indata[:, 0])
        except Exception as e:
            self.error = str(e)

    def _on_state(self, st):
        self._latest = st

    def latest(self):
        return self._latest

    @property
    def running(self):
        return self.stream is not None

    def stop(self):
        if self.stream is not None:
            try:
                self.stream.stop(); self.stream.close()
            except Exception:
                pass
        self.stream = None


def _moyu_mode(vals):
    """Most common value (the real reading dominates the scattered bit-errors)."""
    if not vals:
        return 0
    counts = {}; best = vals[-1]; bestn = 0
    for v in vals:
        n = counts.get(v, 0) + 1; counts[v] = n
        if n > bestn:
            bestn = n; best = v
    return best

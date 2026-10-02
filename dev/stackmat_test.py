#!/usr/bin/env python
"""
Diagnostyka timera audio — MoYu Timer + StackMat.
Uruchom:  py stackmat_test.py
Wybierz tryb (MoYu / StackMat), wejście audio, START i zrób solve.
"""
import math
import tkinter as tk
import customtkinter as ctk

try:
    import sounddevice as sd
    import numpy as np
except Exception as e:
    raise SystemExit("Brak sounddevice/numpy:  py -m pip install sounddevice numpy\n" + str(e))


class AudioTimerDecoder:
    """Port csTimer: tryb 'm' = MoYu (8000, 24-bit BCD), 's' = StackMat (1200 UART)."""
    def __init__(self, sample_rate, mode, on_state):
        self.mode = mode
        div = 8000.0 if mode == 'm' else 1200.0
        self.spb = sample_rate / div
        self.agc_factor = 0.001 / self.spb
        self.last_power = 1.0
        self.lastVal = [0.0] * max(1, math.ceil(self.spb / 6))
        self.lastSgn = 0; self.lenKeep = 0
        self.T_SCHM = 0.2; self.T_EDGE = 0.7
        self.bitBuf = []; self.byteBuf = []
        self.idle_val = 0; self.last_bit = 0; self.last_bit_len = 0; self.no_state_len = 0
        self.state = {'on':False,'time_milli':0,'running':False,'signalHeader':'I',
                      'greenLight':False,'leftHand':False,'rightHand':False,'unit':1}
        self.cb = on_state
        self.raw_bytes = []; self.byte_count = 0; self.readings = 0

    def feed(self, samples):
        for s in samples:
            p = s * s
            self.last_power = max(1e-4, self.last_power + (p - self.last_power) * self.agc_factor)
            self._proc(s / math.sqrt(self.last_power))

    def _proc(self, signal):
        self.lastVal.insert(0, signal); popped = self.lastVal.pop()
        sgn = 1 if self.lastSgn else -1
        isEdge = ((popped - signal) * sgn > self.T_EDGE
                  and abs(signal - sgn) - 1 > self.T_SCHM and self.lenKeep > self.spb * 0.6)
        if isEdge:
            for _ in range(round(self.lenKeep / self.spb)):
                (self._bit_moyu if self.mode == 'm' else self._bit_stk)(self.lastSgn)
            self.lastSgn ^= 1; self.lenKeep = 0
        elif self.lenKeep > self.spb * 2:
            (self._bit_moyu if self.mode == 'm' else self._bit_stk)(self.lastSgn)
            self.lenKeep -= self.spb
        self.lenKeep += 1

    # ── MoYu: 24 bits -> 6 BCD digits = time in ms ──
    def _bit_moyu(self, bit):
        if self.last_bit != self.idle_val and self.last_bit_len == 1:
            self.bitBuf.append(bit)
            if len(self.bitBuf) == 24:
                t = 0
                for i in range(5, -1, -1):
                    t *= 10
                    for j in range(4):
                        t += self.bitBuf[i*4 + j] << j
                self.bitBuf = []
                self._push('S', t, 1)
        if bit != self.last_bit:
            self.last_bit = bit; self.last_bit_len = 1
        else:
            self.last_bit_len += 1
        if self.last_bit_len > 10:
            self.idle_val = bit; self.bitBuf = []; self.byteBuf = []
            if self.last_bit_len > 1000 and self.state['on']:
                self.state['on'] = False; self._emit()
            elif self.last_bit_len > 4000:
                self.last_bit_len = 1000; self._emit()

    # ── StackMat: UART 1200, 9/10-byte packet ──
    def _bit_stk(self, bit):
        self.bitBuf.append(bit)
        if bit != self.last_bit: self.last_bit = bit; self.last_bit_len = 1
        else: self.last_bit_len += 1
        self.no_state_len += 1
        if self.last_bit_len > 10:
            self.idle_val = bit; self.bitBuf = []
            if self.byteBuf: self.byteBuf = []
            if self.last_bit_len > 100 and self.state['on']:
                self.state['on'] = False; self._emit()
            elif self.no_state_len > 700:
                self.no_state_len = 100; self._emit()
        elif len(self.bitBuf) == 10:
            if self.bitBuf[0] == self.idle_val or self.bitBuf[9] != self.idle_val:
                self.bitBuf = self.bitBuf[1:]
            else:
                val = 0
                for i in range(8, 0, -1):
                    val = (val << 1) | (1 if self.bitBuf[i] == self.idle_val else 0)
                ch = chr(val); self.byteBuf.append(ch); self.byte_count += 1
                self.raw_bytes.append(ch if 32 <= val < 127 else '.')
                if len(self.raw_bytes) > 24: self.raw_bytes.pop(0)
                self._decode_stk(); self.bitBuf = []

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
        self._push(bb[0], mm*60000 + ss*1000 + ms, 10 if len(bb) == 9 else 1)

    def _push(self, head, t, unit):
        prev = self.state
        inc = (t > prev['time_milli']) if unit == prev['unit'] else (t // 10 > prev['time_milli'] // 10)
        self.state = {'time_milli':t,'unit':unit,'on':True,'greenLight':head=='A',
                      'leftHand':head in 'LAC','rightHand':head in 'RAC',
                      'running':(head!='S' or prev['signalHeader']=='S') and (head==' ' or inc),
                      'signalHeader':head}
        self.no_state_len = 0; self.readings += 1; self._emit()

    def _emit(self):
        self.cb(dict(self.state))


def fmt(ms):
    m, ms = divmod(int(ms), 60000); s, ms = divmod(ms, 1000)
    return (f"{m}:{s:02d}.{ms:03d}" if m else f"{s}.{ms:03d}")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Timer audio — diagnostyka (MoYu / StackMat)")
        self.geometry("560x600")
        self.stream = None; self.dec = None; self.latest = None
        self.blocks = 0; self.peak = 0.0; self.sr = 0; self.err = ""
        self.wave = []; self.clip = 0.0

        ctk.CTkLabel(self, text="Diagnostyka timera audio",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 2))

        row = ctk.CTkFrame(self, fg_color="transparent"); row.pack(pady=4)
        ctk.CTkLabel(row, text="Tryb:").pack(side="left", padx=(0, 6))
        self.mode_var = ctk.StringVar(value="MoYu")
        ctk.CTkOptionMenu(row, variable=self.mode_var, values=["MoYu", "StackMat"], width=120,
                          command=lambda _:( self._stop() if self.stream else None)).pack(side="left")

        self.devs = self._input_devices()
        names = [f"[{i}] {n}" for i, n in self.devs]
        self.dev_var = ctk.StringVar(value=names[0] if names else "(brak)")
        ctk.CTkOptionMenu(self, variable=self.dev_var, values=names, width=520).pack(pady=8)
        self.btn = ctk.CTkButton(self, text="▶  START", command=self._toggle, width=160, height=34)
        self.btn.pack()

        ctk.CTkLabel(self, text="① Poziom sygnału (czy cokolwiek dociera):",
                     font=ctk.CTkFont(size=11), text_color="gray60", anchor="w").pack(fill="x", padx=18, pady=(10, 0))
        self.level_bar = ctk.CTkProgressBar(self, width=520); self.level_bar.set(0); self.level_bar.pack(pady=2)
        self.level_txt = ctk.CTkLabel(self, text="peak: —", font=ctk.CTkFont(size=11), text_color="gray55"); self.level_txt.pack()
        self.wave_canvas = tk.Canvas(self, width=520, height=80, bg="#0d0d18", highlightthickness=0); self.wave_canvas.pack(pady=(4, 0))

        ctk.CTkLabel(self, text="② Zdekodowany czas / stan:",
                     font=ctk.CTkFont(size=11), text_color="gray60", anchor="w").pack(fill="x", padx=18, pady=(8, 0))
        self.time_lbl = ctk.CTkLabel(self, text="—.———", font=ctk.CTkFont(size=46, weight="bold")); self.time_lbl.pack()
        self.status_lbl = ctk.CTkLabel(self, text="odczyty: 0", font=ctk.CTkFont(size=12), text_color="gray60"); self.status_lbl.pack()

        self.diag = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, weight="bold"), wraplength=520, justify="left")
        self.diag.pack(pady=(8, 4), padx=14, fill="x")
        self.after(80, self._tick)

    def _input_devices(self):
        out = []
        try:
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0: out.append((i, d['name']))
        except Exception as e: out.append((-1, f"błąd: {e}"))
        return out

    def _toggle(self):
        if self.stream is not None: self._stop(); return
        try:
            idx = int(self.dev_var.get().split(']')[0][1:])
            info = sd.query_devices(idx); self.sr = int(info['default_samplerate'])
            self.blocks = 0; self.peak = 0.0; self.err = ""
            mode = 'm' if self.mode_var.get() == "MoYu" else 's'
            self.dec = AudioTimerDecoder(self.sr, mode, self._on_state)
            self.stream = sd.InputStream(device=idx, channels=1, samplerate=self.sr,
                                         blocksize=2048, dtype='float32', callback=self._audio)
            self.stream.start()
            self.btn.configure(text="■  STOP", fg_color="#a33")
        except Exception as e:
            self.err = str(e); self.diag.configure(text=f"BŁĄD: {e}", text_color="#f66")

    def _stop(self):
        try: self.stream.stop(); self.stream.close()
        except Exception: pass
        self.stream = None; self.btn.configure(text="▶  START", fg_color=["#3a7ebf", "#1f6aa5"])

    def _audio(self, indata, frames, t, status):
        try:
            ch = indata[:, 0]
            pk = float(np.max(np.abs(ch))) if len(ch) else 0.0
            self.peak = max(pk, self.peak * 0.85)
            self.clip = float(np.mean(np.abs(ch) > 0.985)) if len(ch) else 0.0
            step = max(1, len(ch) // 480); self.wave = ch[::step][:480].tolist()
            self.blocks += 1
            if self.dec is not None: self.dec.feed(ch)
        except Exception as e:
            self.err = str(e)

    def _on_state(self, st): self.latest = st

    def _tick(self):
        running = self.stream is not None
        self.level_bar.set(min(1.0, self.peak))
        self.level_txt.configure(text=f"peak: {self.peak:.4f}   clipping: {int(self.clip*100)}%   bloki: {self.blocks}   SR: {self.sr}")
        c = self.wave_canvas; c.delete("all"); W, H = 520, 80
        c.create_line(0, H/2, W, H/2, fill="#333")
        if self.wave:
            n = len(self.wave); co = []
            for i, v in enumerate(self.wave):
                co += [i*W/(n-1), H/2 - max(-1, min(1, v))*(H*0.46)]
            if len(co) >= 4: c.create_line(*co, fill="#5cf")
        st = self.latest
        if st is not None: self.time_lbl.configure(text=fmt(st['time_milli']))
        if self.dec is not None:
            self.status_lbl.configure(text=f"odczyty: {self.dec.readings}   (tryb {self.mode_var.get()})")

        msg, col = "", "gray70"
        if not running: msg = "Wybierz TRYB (MoYu), wejście i kliknij START."
        elif self.err: msg = "Błąd: " + self.err; col = "#f66"
        elif self.blocks < 2: msg = "Strumień nie rusza — wybierz inne wejście."; col = "#fa0"
        elif self.peak < 0.002:
            msg = "BRAK SYGNAŁU (peak~0). Złe wejście albo jack nie w tym gnieździe — spróbuj innego wejścia z listy."; col = "#fa0"
        elif self.clip > 0.3:
            msg = f"PRZESTER ({int(self.clip*100)}%)! Ściągnij 'Wzmocnienie mikrofonu' do 0 dB i głośność do ~40%."; col = "#fa0"
        elif self.dec and self.dec.readings == 0:
            msg = "Sygnał jest, ale brak odczytów. Zrób solve i patrz na falę. Jeśli nic → spróbuj drugiego trybu lub innego wejścia."; col = "#fa0"
        else:
            msg = f"DZIAŁA ✓  odczyty: {self.dec.readings}. Rób solve — czas powinien się pojawiać."; col = "#5d5"
        self.diag.configure(text=msg, text_color=col)
        self.after(80, self._tick)


if __name__ == "__main__":
    App().mainloop()

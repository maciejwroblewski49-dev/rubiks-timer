"""Where rubik-timer data lives on disk, and the Config/Sessions classes that read/write it."""
import os, sys, json, copy, threading, atexit
from datetime import datetime

# Support running as a PyInstaller .exe (frozen) or as a plain .py script
if getattr(sys, "frozen", False):
    BASE_DIR  = os.path.dirname(sys.executable)
    _ASSETS   = sys._MEIPASS
else:
    BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
    _ASSETS   = BASE_DIR

# User data (sessions, times, colours/settings) lives in a FIXED folder in the
# user's home directory — NOT next to the program and NOT under AppData — so
# rebuilding/replacing the .exe never wipes them, and it is never affected by
# any app-sandbox AppData virtualisation.
DATA_DIR = os.path.join(os.path.expanduser("~"), "Rubiks Timer")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    DATA_DIR = BASE_DIR

DATA_FILE   = os.path.join(DATA_DIR, "sessions.json")
CFG_FILE    = os.path.join(DATA_DIR, "settings.json")
ICON_FILE   = os.path.join(_ASSETS,  "icon.ico")

def _migrate_legacy_data():
    """First run: copy sessions/settings from an old install location."""
    import shutil
    legacy = [BASE_DIR,
              os.path.join(os.environ.get("APPDATA") or "", "Rubiks Timer"),
              os.path.dirname(os.path.abspath(__file__))]
    for fname in ("sessions.json", "settings.json"):
        dst = os.path.join(DATA_DIR, fname)
        if os.path.exists(dst):
            continue
        for ld in legacy:
            src = os.path.join(ld, fname)
            if ld and os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
                try:
                    shutil.copy2(src, dst); break
                except Exception:
                    pass
_migrate_legacy_data()


DEFAULTS = {
    "theme": "dark",
    "colors": {
        "timer_idle":       "#FFFFFF",
        "timer_ready":      "#FF4444",
        "timer_running":    "#44DD77",
        "timer_inspection": "#FFAA00",
        "timer_penalty":    "#FF4444",
        "scramble":         "#DDDDDD",
        "bg_window":        "",
        "bg_header":        "",
    },
    "timer": {
        "inspection_enabled":  True,
        "inspection_duration": 15,
        "hide_during_solve":   False,
        "start_delay_ms":      0,
        "decimals":            3,
        "refresh_ms":          30,
        "autosize":            True,
        "hide_ui_while_solving": False,
    },
    "stats": {
        "show_best":       True,
        "show_ao5":        True,
        "show_ao12":       True,
        "show_ao100":      False,
        "show_mean":       True,
        "custom_averages": [],
        "trim_mode":       "wca",     # "wca" = ceil(5%) z każdej strony, "one" = zawsze 1
        "show_best_avg":   True,
    },
    "font": {
        "timer_size":      88,
        "scramble_size":   15,
        "timer_family":    "Default",
        "scramble_family": "Default",
    },
    "show_main_viz": False,
    "ui_zoom":       1.0,
    "accent":        "Niebieski",
    "layout": {
        "preset":  "Klasyczny",
        "gap":     8,
        "radius":  14,
        "borders": True,
        "snap":    True,
        "panels":  {},          # filled from ui.layout.PRESETS on first run
    },
    "times_list": {
        "columns":         ["ao5", "ao12"],
        "density":         "normal",     # compact / normal / comfy
        "smooth_scroll":   True,
        "highlight_pb":    True,
        "mono_digits":     False,
        "show_raw_on_dnf": False,
    },
    "scramble_align": "center",
    "target": {
        "enabled": False,
        "time":    10.0,
        "pb_sound": True,
    },
    "moyu": {
        "enabled": False,
        "device":  "",
        "type":    "m",          # 'm' = MoYu, 's' = StackMat Gen3/4/5 (jack)
    },
}


def _atomic_write(path, text):
    """Write via a temp file + rename, so a crash mid-write never leaves a
    half-written (unreadable) sessions.json behind."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def _merge(base, over):
    r = copy.deepcopy(base)
    for k, v in over.items():
        if k in r and isinstance(r[k], dict) and isinstance(v, dict):
            r[k] = _merge(r[k], v)
        else:
            r[k] = v
    return r


class Config:
    def __init__(self):
        self._d = self._load()
        self._save_timer = None
        self._save_lock = threading.Lock()
        atexit.register(self.flush)

    def _load(self):
        if os.path.exists(CFG_FILE):
            try:
                with open(CFG_FILE,"r",encoding="utf-8") as f:
                    return _merge(DEFAULTS, json.load(f))
            except Exception: pass
        return copy.deepcopy(DEFAULTS)

    def _write_now(self):
        _atomic_write(CFG_FILE, json.dumps(self._d, ensure_ascii=False, indent=2))

    def save(self, delay=0.4):
        # Debounced: collapses rapid-fire saves (e.g. dragging a settings
        # slider fires this on every pixel) into a single disk write, off
        # the UI thread.
        with self._save_lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
            self._save_timer = threading.Timer(delay, self._write_now)
            self._save_timer.daemon = True
            self._save_timer.start()

    def flush(self):
        """Write immediately and cancel any pending debounced save. Runs at exit."""
        with self._save_lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
                self._save_timer = None
        self._write_now()

    def g(self, *keys):
        d = self._d
        for k in keys: d = d[k]
        return d

    def s(self, *args):
        keys, val = args[:-1], args[-1]
        d = self._d
        for k in keys[:-1]: d = d[k]
        d[keys[-1]] = val
        self.save()

# ══════════════════════════════════════════════════════════════════
#  Sessions
# ══════════════════════════════════════════════════════════════════

class Sessions:
    def __init__(self):
        self._d = self._load()
        self._save_timer = None
        self._save_lock = threading.Lock()
        atexit.register(self.flush)

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
            except Exception: pass
        name = f"Sesja {datetime.now().strftime('%d.%m.%Y')}"
        return {"last": name, "sessions": {name: {"puzzle":"3x3","times":[]}}}

    def _write_now(self):
        # No indent: with indent= json falls back to its pure-Python encoder,
        # which on a big sessions.json held the GIL long enough to stutter the
        # UI right after a solve.  The C encoder is ~10x faster.
        _atomic_write(DATA_FILE, json.dumps(self._d, ensure_ascii=False,
                                            separators=(",", ":")))

    def _save(self, delay=0.4):
        # Debounced + off the UI thread: sessions.json is 190KB+ and growing;
        # rewriting it synchronously on every solve was blocking the UI thread
        # right at the moment a solve finishes (see _record()).
        with self._save_lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
            self._save_timer = threading.Timer(delay, self._write_now)
            self._save_timer.daemon = True
            self._save_timer.start()

    def flush(self):
        """Write immediately and cancel any pending debounced save. Runs at exit."""
        with self._save_lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
                self._save_timer = None
        self._write_now()

    @property
    def names(self):  return list(self._d["sessions"].keys())
    @property
    def last(self):   return self._d["last"]

    def get(self, n):             return self._d["sessions"][n]
    def create(self, n, p="3x3"):
        self._d["sessions"][n] = {"puzzle":p,"times":[]}
        self._d["last"] = n; self._save()
    def switch(self, n):          self._d["last"] = n; self._save()
    def set_puzzle(self, n, p):   self._d["sessions"][n]["puzzle"] = p; self._save()
    def rename(self, old, new):
        self._d["sessions"][new] = self._d["sessions"].pop(old)
        if self._d["last"] == old: self._d["last"] = new
        self._save()
    def delete_session(self, n):
        self._d["sessions"].pop(n, None)
        if self._d["last"] == n:
            self._d["last"] = self.names[0] if self.names else ""
        self._save()
    def get_notes(self, n):        return self._d["sessions"][n].get("notes","")
    def set_notes(self, n, text): self._d["sessions"][n]["notes"] = text; self._save()
    def add(self, n, e):          self._d["sessions"][n]["times"].append(e); self._save()
    def update(self, n, i, e):    self._d["sessions"][n]["times"][i] = e; self._save()
    def delete(self, n, i):       self._d["sessions"][n]["times"].pop(i); self._save()

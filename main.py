# ── Single-instance guard — runs FIRST (before heavy imports).  A second copy
# launched from the shortcut detects the running instance in <100 ms, raises
# its window and exits, without waiting to load customtkinter/tkinter first.
import os, sys, ctypes, atexit
try:
    _LOCK_DIR = os.path.join(os.path.expanduser("~"), "Rubiks Timer")
    os.makedirs(_LOCK_DIR, exist_ok=True)
    _LOCK_FILE = os.path.join(_LOCK_DIR, ".app.lock")
    _k = ctypes.WinDLL("kernel32")
    _k.OpenProcess.restype  = ctypes.c_void_p
    _k.OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
    _k.CloseHandle.argtypes = [ctypes.c_void_p]
    def _pid_alive(pid):
        try:
            h = _k.OpenProcess(0x1000, 0, int(pid))
            if h: _k.CloseHandle(h); return True
        except Exception: pass
        return False
    if os.path.exists(_LOCK_FILE):
        try:
            with open(_LOCK_FILE) as _lf: _old = int(_lf.read().strip() or "0")
        except Exception: _old = 0
        if _old and _old != os.getpid() and _pid_alive(_old):
            for _title in ("Wróbel Timer", "Rubik's Timer", "Rubiks Timer"):
                _hwnd = ctypes.windll.user32.FindWindowW(None, _title)
                if _hwnd:
                    ctypes.windll.user32.ShowWindow(_hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(_hwnd)
                    break
            sys.exit(0)
    with open(_LOCK_FILE, "w") as _lf: _lf.write(str(os.getpid()))
    atexit.register(lambda p=_LOCK_FILE: os.path.exists(p) and os.remove(p))
except SystemExit: raise
except Exception: pass

from app import App

if __name__ == "__main__":
    App().mainloop()

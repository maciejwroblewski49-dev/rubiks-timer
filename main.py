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

import customtkinter as ctk
import time, random, json, csv, copy, zipfile, threading, math
from datetime import datetime
import tkinter as tk
import tkinter.simpledialog as sd
import tkinter.colorchooser as cc
import tkinter.filedialog as fd
import tkinter.messagebox as mb


# matplotlib is only used inside the Tools window (charts + histogram).  Importing
# it eagerly adds ~500 ms to the cold startup — instead we load it lazily the
# first time a chart is actually built.









# ══════════════════════════════════════════════════════════════════
#  Scramble generators
# ══════════════════════════════════════════════════════════════════







# ══════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════



# ══════════════════════════════════════════════════════════════════
#  Config
# ══════════════════════════════════════════════════════════════════










# ══════════════════════════════════════════════════════════════════
#  Manual time entry dialog
# ══════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════
#  Cube state — 3×3 simulator + 2D net drawing
# ══════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════
#  Time detail dialog  (left-click on a time in the list)
# ══════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════
#  Stat detail dialog  (ao5/ao12/ao100/mean/best breakdown)
# ══════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════
#  Settings window
# ══════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════
#  Tools window
# ══════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════
#  Main App
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#  External hardware timer over the audio jack (MoYu / StackMat)
# ══════════════════════════════════════════════════════════════════





from app import App

if __name__ == "__main__":
    App().mainloop()

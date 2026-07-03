"""Small, dependency-free helpers shared across rubik-timer modules."""
try:
    import winsound as _winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False


def fmt(sec, dec=3):
    if sec >= 60:
        m = int(sec // 60); s = sec % 60
        return f"{m}:{s:0{dec+3}.{dec}f}"
    return f"{sec:.{dec}f}"

def display(entry, dec=3):
    p = entry.get("penalty")
    if p in ("DNF","DNS"): return p
    return fmt(entry["time"] + (2 if p=="+2" else 0), dec)

def effective(entry):
    p = entry.get("penalty")
    if p in ("DNF","DNS"): return float("inf")
    return entry["time"] + (2 if p=="+2" else 0)


def _bring_to_front(win):
    """Force a CTkToplevel window to appear on top and grab focus on Windows."""
    win.attributes("-topmost", True)
    win.lift()
    win.focus_force()
    win.after(300, lambda: win.attributes("-topmost", False) if win.winfo_exists() else None)

"""Free-form panel layout: every panel of the main window sits at a relative
rectangle (0..1 of the content area) that you can drag and resize yourself.

Normal mode just place()s the panels.  Edit mode adds a grab bar on top of
each panel (drag = move), a corner grip (drag = resize) and snaps edges to
the window, the centre line and the other panels so things line up by
themselves.
"""
import copy
import tkinter as tk
import customtkinter as ctk

from ui import theme
from ui.theme import C

PANELS = ("scramble", "timer", "stats", "times", "viz")
PANEL_NAMES = {
    "scramble": "Scramble",
    "timer":    "Timer",
    "stats":    "Statystyki",
    "times":    "Lista czasów",
    "viz":      "Podgląd kostki",
}

def _p(x, y, w, h, visible=True):
    return {"x": x, "y": y, "w": w, "h": h, "visible": visible}

# Each preset has two variants: without the cube preview, and with it (then
# the preview gets its own slot instead of covering the timer).
PRESETS = {
    "Klasyczny": ({
        "scramble": _p(0.00, 0.00, 1.00, 0.16),
        "timer":    _p(0.00, 0.16, 0.73, 0.60),
        "stats":    _p(0.00, 0.76, 0.73, 0.24),
        "times":    _p(0.73, 0.16, 0.27, 0.84),
    }, {
        "scramble": _p(0.00, 0.00, 1.00, 0.16),
        "viz":      _p(0.00, 0.16, 0.22, 0.60),
        "timer":    _p(0.22, 0.16, 0.51, 0.60),
        "stats":    _p(0.00, 0.76, 0.73, 0.24),
        "times":    _p(0.73, 0.16, 0.27, 0.84),
    }),
    "Lista z lewej": ({
        "scramble": _p(0.00, 0.00, 1.00, 0.16),
        "times":    _p(0.00, 0.16, 0.27, 0.84),
        "timer":    _p(0.27, 0.16, 0.73, 0.60),
        "stats":    _p(0.27, 0.76, 0.73, 0.24),
    }, {
        "scramble": _p(0.00, 0.00, 1.00, 0.16),
        "times":    _p(0.00, 0.16, 0.27, 0.84),
        "timer":    _p(0.27, 0.16, 0.51, 0.60),
        "viz":      _p(0.78, 0.16, 0.22, 0.60),
        "stats":    _p(0.27, 0.76, 0.73, 0.24),
    }),
    "Statystyki z boku": ({
        "scramble": _p(0.00, 0.00, 0.72, 0.18),
        "timer":    _p(0.00, 0.18, 0.72, 0.82),
        "stats":    _p(0.72, 0.00, 0.28, 0.46),
        "times":    _p(0.72, 0.46, 0.28, 0.54),
    }, {
        "scramble": _p(0.00, 0.00, 0.72, 0.18),
        "timer":    _p(0.00, 0.18, 0.72, 0.56),
        "viz":      _p(0.00, 0.74, 0.72, 0.26),
        "stats":    _p(0.72, 0.00, 0.28, 0.46),
        "times":    _p(0.72, 0.46, 0.28, 0.54),
    }),
    "Wszystko na dole": ({
        "scramble": _p(0.00, 0.00, 1.00, 0.16),
        "timer":    _p(0.00, 0.16, 1.00, 0.52),
        "stats":    _p(0.00, 0.68, 0.62, 0.32),
        "times":    _p(0.62, 0.68, 0.38, 0.32),
    }, {
        "scramble": _p(0.00, 0.00, 1.00, 0.16),
        "timer":    _p(0.00, 0.16, 1.00, 0.52),
        "viz":      _p(0.00, 0.68, 0.24, 0.32),
        "stats":    _p(0.24, 0.68, 0.42, 0.32),
        "times":    _p(0.66, 0.68, 0.34, 0.32),
    }),
    "Minimalny": ({
        "scramble": _p(0.06, 0.00, 0.88, 0.16),
        "timer":    _p(0.00, 0.16, 1.00, 0.66),
        "stats":    _p(0.10, 0.82, 0.80, 0.18),
    }, {
        "scramble": _p(0.06, 0.00, 0.88, 0.16),
        "viz":      _p(0.00, 0.16, 0.24, 0.66),
        "timer":    _p(0.24, 0.16, 0.76, 0.66),
        "stats":    _p(0.10, 0.82, 0.80, 0.18),
    }),
}
DEFAULT_PRESET = "Klasyczny"
CUSTOM = "Własny"

# Focus mode (◉ / F) temporarily uses this instead of the saved layout.
FOCUS_LAYOUT = {
    "scramble": _p(0.06, 0.00, 0.88, 0.18),
    "timer":    _p(0.00, 0.18, 1.00, 0.82),
}

MIN_W, MIN_H = 0.10, 0.08
SNAP_PX = 10


def preset(name, viz=False):
    """Full rect dict for a preset; panels a preset doesn't use come back hidden."""
    variants = PRESETS.get(name, PRESETS[DEFAULT_PRESET])
    rects = copy.deepcopy(variants[1] if viz else variants[0])
    fallback = PRESETS[DEFAULT_PRESET][1]
    for pid in PANELS:
        if pid not in rects:
            rects[pid] = dict(fallback[pid], visible=False)
    return rects


class LayoutManager:

    def __init__(self, app, area, frames):
        self.app = app
        self.cfg = app.cfg
        self.area = area
        self.frames = frames                 # pid -> CTkFrame
        self.editing = False
        self.override = None                 # temporary layout (focus mode)
        self._handles = {}
        self._grips = {}
        self._drag = None
        self._ensure_config()

    # ── config ────────────────────────────────────────────────────

    def _ensure_config(self):
        panels = self.cfg.g("layout", "panels")
        base = preset(self.cfg.g("layout", "preset"), bool(self.cfg.g("show_main_viz")))
        changed = False
        for pid in PANELS:
            if pid not in panels or not all(k in panels[pid] for k in ("x", "y", "w", "h", "visible")):
                panels[pid] = base[pid]; changed = True
        if changed:
            self.cfg.s("layout", "panels", panels)

    def rect(self, pid):
        src = self.override if self.override is not None else self.cfg.g("layout", "panels")
        return src.get(pid)

    def visible(self, pid):
        r = self.rect(pid)
        return bool(r and r["visible"])

    def set_visible(self, pid, on):
        if pid == "viz":
            self.cfg.s("show_main_viz", bool(on))
            # on a built-in preset the preview gets its own slot, and the
            # other panels take the space back when it is hidden again
            if self.cfg.g("layout", "preset") in PRESETS:
                self.load_preset(self.cfg.g("layout", "preset"))
                return
        panels = self.cfg.g("layout", "panels")
        panels[pid]["visible"] = bool(on)
        self.cfg.s("layout", "panels", panels)
        if pid != "viz":
            self.cfg.s("layout", "preset", CUSTOM)
        self.apply()

    def load_preset(self, name):
        p = preset(name, bool(self.cfg.g("show_main_viz")))
        self.cfg.s("layout", "preset", name)
        self.cfg.s("layout", "panels", p)
        self.apply()

    # ── placing ───────────────────────────────────────────────────

    def _gap(self):
        return int(self.cfg.g("layout", "gap"))

    def place(self, pid):
        f = self.frames[pid]
        r = self.rect(pid)
        if not r or not r["visible"]:
            f.place_forget()
            self._place_overlay(pid, None)
            return
        g = self._gap() / 2
        # tk's own place(): customtkinter's wrapper refuses width/height,
        # which we need (negative) to keep a gap between panels
        tk.Place.place_configure(f, relx=r["x"], rely=r["y"], relwidth=r["w"],
                                 relheight=r["h"], x=g, y=g, width=-2 * g, height=-2 * g)
        self._place_overlay(pid, r)

    def apply(self):
        for pid in PANELS:
            self.place(pid)
        # the cube preview is usually small and floats over the timer
        if self.visible("viz"):
            self.frames["viz"].lift()
        if self.editing:
            self._rebuild_overlays()
        self.app._on_layout_changed()

    # ── edit mode ─────────────────────────────────────────────────

    def set_editing(self, on):
        self.editing = bool(on)
        acc = theme.accent(self.cfg)
        for pid, f in self.frames.items():
            if self.editing:
                f.configure(border_width=2, border_color=acc)
            else:
                f.configure(border_width=1 if self.cfg.g("layout", "borders") else 0,
                            border_color=C["border"])
        self._rebuild_overlays()

    def _rebuild_overlays(self):
        for w in list(self._handles.values()) + list(self._grips.values()):
            w.destroy()
        self._handles.clear(); self._grips.clear()
        if not self.editing:
            return
        acc = theme.accent(self.cfg)
        for pid in PANELS:
            if not self.visible(pid):
                continue
            bar = ctk.CTkFrame(self.area, height=28, corner_radius=8, fg_color=acc)
            lbl = ctk.CTkLabel(bar, text=f"  ⠿  {PANEL_NAMES[pid]}", text_color="white",
                               font=theme.font(12, "bold"), cursor="fleur", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            hide = ctk.CTkButton(bar, text="✕", width=24, height=22, corner_radius=6,
                                 fg_color="transparent", hover_color=theme.mix(acc[1], "#000000", 0.25),
                                 text_color="white", font=theme.font(12, "bold"),
                                 command=lambda p=pid: self.set_visible(p, False))
            hide.pack(side="right", padx=3)
            for w in (bar, lbl):
                w.bind("<ButtonPress-1>", lambda e, p=pid: self._press(e, p, "move"))
                w.bind("<B1-Motion>", self._motion)
                w.bind("<ButtonRelease-1>", self._release)
            grip = ctk.CTkLabel(self.area, text="◢", width=22, height=22, corner_radius=6,
                                fg_color=acc, text_color="white", font=theme.font(13),
                                cursor="bottom_right_corner")
            grip.bind("<ButtonPress-1>", lambda e, p=pid: self._press(e, p, "resize"))
            grip.bind("<B1-Motion>", self._motion)
            grip.bind("<ButtonRelease-1>", self._release)
            self._handles[pid] = bar
            self._grips[pid] = grip
            self._place_overlay(pid, self.rect(pid))

    def _place_overlay(self, pid, r):
        bar, grip = self._handles.get(pid), self._grips.get(pid)
        if not bar:
            return
        if r is None or not r["visible"]:
            bar.place_forget(); grip.place_forget(); return
        g = self._gap() / 2 + 4
        tk.Place.place_configure(bar, relx=r["x"], rely=r["y"], relwidth=r["w"],
                                 x=g, y=g, width=-2 * g)
        grip.place(relx=r["x"] + r["w"], rely=r["y"] + r["h"], x=-g, y=-g, anchor="se")
        bar.lift(); grip.lift()

    # ── dragging ──────────────────────────────────────────────────

    def _press(self, e, pid, mode):
        r = self.cfg.g("layout", "panels")[pid]
        self._drag = {"pid": pid, "mode": mode, "x0": e.x_root, "y0": e.y_root,
                      "r0": dict(r)}
        self.frames[pid].lift()
        self._place_overlay(pid, r)

    def _snap_targets(self, pid):
        xs, ys = {0.0, 0.5, 1.0}, {0.0, 0.5, 1.0}
        for other, r in self.cfg.g("layout", "panels").items():
            if other == pid or not r["visible"]:
                continue
            xs.update((r["x"], r["x"] + r["w"]))
            ys.update((r["y"], r["y"] + r["h"]))
        return xs, ys

    @staticmethod
    def _snap(v, targets, tol):
        best = min(targets, key=lambda t: abs(t - v))
        return best if abs(best - v) <= tol else v

    @staticmethod
    def _snap_pos(pos, size, targets, tol):
        """Snap a panel's start or end edge (whichever is closer) to a target."""
        best, bd = pos, tol
        for t in targets:
            for cand in (t, t - size):
                if abs(cand - pos) <= bd:
                    best, bd = cand, abs(cand - pos)
        return best

    def _motion(self, e):
        d = self._drag
        if not d:
            return
        W = max(1, self.area.winfo_width()); H = max(1, self.area.winfo_height())
        dx = (e.x_root - d["x0"]) / W
        dy = (e.y_root - d["y0"]) / H
        r0 = d["r0"]
        r = self.cfg.g("layout", "panels")[d["pid"]]
        snap = self.cfg.g("layout", "snap")
        tx, ty = self._snap_targets(d["pid"]) if snap else (set(), set())
        tolx, toly = SNAP_PX / W, SNAP_PX / H
        if d["mode"] == "move":
            x = min(max(0.0, r0["x"] + dx), 1 - r0["w"])
            y = min(max(0.0, r0["y"] + dy), 1 - r0["h"])
            if snap:
                x = min(max(0.0, self._snap_pos(x, r0["w"], tx, tolx)), 1 - r0["w"])
                y = min(max(0.0, self._snap_pos(y, r0["h"], ty, toly)), 1 - r0["h"])
            r["x"], r["y"] = round(x, 4), round(y, 4)
        else:
            right = min(1.0, max(r0["x"] + MIN_W, r0["x"] + r0["w"] + dx))
            bottom = min(1.0, max(r0["y"] + MIN_H, r0["y"] + r0["h"] + dy))
            if snap:
                right = self._snap(right, tx, tolx)
                bottom = self._snap(bottom, ty, toly)
            r["w"] = round(max(MIN_W, right - r0["x"]), 4)
            r["h"] = round(max(MIN_H, bottom - r0["y"]), 4)
        self.place(d["pid"])

    def _release(self, _e):
        if not self._drag:
            return
        self._drag = None
        self.cfg.s("layout", "preset", CUSTOM)
        self.cfg.s("layout", "panels", self.cfg.g("layout", "panels"))
        self.app._on_layout_changed()

"""Record celebration: confetti / fireworks / glow plus a "NEW RECORD" banner.

Tk can't draw see-through on top of other widgets, so by default the effect
plays on a canvas laid over the timer panel (it repaints the time itself).
On Windows it can instead use a click-through, colour-keyed window over the
whole app ("na całym oknie").
"""
import math
import random
import sys
import time
import threading
import tkinter as tk

from utils import _HAS_WINSOUND, _winsound
from ui import theme
from ui.theme import C, pick

COLORS = ["#f43f5e", "#f59e0b", "#facc15", "#22c55e", "#06b6d4",
          "#6366f1", "#a855f7", "#ec4899", "#ffffff"]
STYLES = {"Konfetti": "confetti", "Fajerwerki": "fireworks", "Delikatny błysk": "glow"}
_KEY = "#010203"          # transparent colour of the whole-window overlay

FANFARES = {
    "single": [(784, 90), (988, 90), (1175, 90), (1568, 260)],
    "average": [(659, 90), (784, 90), (1047, 220)],
    "target": [(880, 70), (1175, 130)],
}


def play_fanfare(kind):
    if not _HAS_WINSOUND:
        return
    notes = FANFARES.get(kind, FANFARES["average"])
    threading.Thread(target=lambda: [_winsound.Beep(f, d) for f, d in notes],
                     daemon=True).start()


class Celebration:
    DURATION = 2.8

    def __init__(self, app, title, subtitle="", style="confetti", intensity=1.0,
                 big=True, whole_window=False):
        self.app = app
        self.title = title
        self.subtitle = subtitle
        self.style = style
        self.big = big
        self.alive = True
        self._after = None
        self._top = None
        self.parts = []
        self.bursts = []
        self.n = int((150 if big else 55) * max(0.2, float(intensity)))
        self.scale = app._scale()

        if whole_window and sys.platform == "win32" and self._make_window():
            pass
        else:
            self._make_panel_overlay()

        self.cv.update_idletasks()
        self.W = max(50, self.cv.winfo_width())
        self.H = max(50, self.cv.winfo_height())
        self._draw_banner()
        if style == "confetti":
            self._spawn_confetti()
        elif style == "fireworks":
            t = 0.0
            for _ in range(5 if big else 2):
                self.bursts.append(t)
                t += random.uniform(0.18, 0.4)
        self._t0 = self._last = time.perf_counter()
        self._frame()

    # ── surfaces ──────────────────────────────────────────────────

    def _make_panel_overlay(self):
        f = self.app._panels["timer"]
        inset = max(2, int(int(self.app.cfg.g("layout", "radius")) * 0.35) + 1)
        self.bg = pick(C["panel"])
        self.cv = tk.Canvas(f, highlightthickness=0, bd=0, bg=self.bg)
        tk.Place.place_configure(self.cv, x=inset, y=inset, relwidth=1, relheight=1,
                                 width=-2 * inset, height=-2 * inset)
        self.cv.update_idletasks()
        # the overlay hides the label, so paint the time ourselves
        lbl = self.app.timer_lbl
        cx = lbl.winfo_x() + lbl.winfo_width() / 2 - inset
        cy = lbl.winfo_y() + lbl.winfo_height() / 2 - inset
        fnt = self.app._timer_font
        self.timer_item = self.cv.create_text(
            cx, cy, text=self.app.timer_var.get(), fill=pick(C["gold"]),
            font=(fnt.cget("family"), -int(fnt.cget("size") * self.scale), "bold"))
        self.center = (cx, cy)

    def _make_window(self):
        app = self.app
        try:
            top = tk.Toplevel(app)
            top.overrideredirect(True)
            top.configure(bg=_KEY)
            top.attributes("-transparentcolor", _KEY)
            top.attributes("-topmost", True)
            try:
                top.attributes("-disabled", True)      # never takes clicks or focus
            except tk.TclError:
                pass
            top.geometry(f"{app.winfo_width()}x{app.winfo_height()}"
                         f"+{app.winfo_rootx()}+{app.winfo_rooty()}")
        except tk.TclError:
            return False
        self._top = top
        self.bg = _KEY
        self.cv = tk.Canvas(top, highlightthickness=0, bd=0, bg=_KEY)
        self.cv.pack(fill="both", expand=True)
        f = app._panels["timer"]
        self.center = (f.winfo_rootx() - app.winfo_rootx() + f.winfo_width() / 2,
                       f.winfo_rooty() - app.winfo_rooty() + f.winfo_height() / 2)
        self.timer_item = None
        app.after(30, app.focus_force)                   # keep SPACE on the timer
        return True

    # ── banner ────────────────────────────────────────────────────

    def _draw_banner(self):
        cx, cy = self.center
        s = self.scale
        if self.timer_item is None:
            y = cy
        else:
            # above the digits if there is room, otherwise over them on a pill
            y = max(44 * s, cy - self._timer_half() - 30 * s)
        fam = theme.ui_family()
        acc = pick(theme.accent(self.app.cfg))
        self.banner_y = y
        self.b_title = self.cv.create_text(cx, y, text=self.title, fill=pick(C["gold"]),
                                           font=(fam, -int(10 * s), "bold"))
        self.b_sub = self.cv.create_text(cx, y + 32 * s, text=self.subtitle,
                                         fill="#ffffff" if self.bg == _KEY else pick(C["text"]),
                                         font=(fam, -int(15 * s), "bold"))
        # a solid rounded pill keeps the text readable over digits / confetti
        sub_w = (self.cv.bbox(self.b_sub) or (0, 0, 300, 0))
        half_w = max(230 * s, (sub_w[2] - sub_w[0]) / 2 + 28 * s)
        x0, y0, x1, y1 = cx - half_w, y - 30 * s, cx + half_w, y + 52 * s
        r = 22 * s
        pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
               x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
        fill = "#111522" if self.bg == _KEY else pick(C["panel_alt"])
        self.pill = self.cv.create_polygon(pts, smooth=True, fill=fill, outline=acc, width=2)
        self.cv.tag_lower(self.pill, self.b_title)

    def _timer_half(self):
        bb = self.cv.bbox(self.timer_item)
        return (bb[3] - bb[1]) / 2 if bb else 60

    # ── particles ─────────────────────────────────────────────────

    def _new(self, x, y, vx, vy, shape="rect"):
        size = random.uniform(5, 10) * self.scale * (1.4 if shape == "dot" else 1)
        col = random.choice(COLORS)
        if shape == "rect":
            item = self.cv.create_polygon(0, 0, 0, 0, 0, 0, fill=col, outline="")
        else:
            item = self.cv.create_oval(0, 0, 0, 0, fill=col, outline="")
        self.parts.append({"x": x, "y": y, "vx": vx, "vy": vy, "rot": random.uniform(0, 6.28),
                           "vr": random.uniform(-9, 9), "flip": random.uniform(0, 6.28),
                           "vf": random.uniform(6, 14), "size": size, "item": item,
                           "shape": shape, "life": 0.0,
                           "max": random.uniform(0.9, 1.5) if shape == "dot" else 99})

    def _spawn_confetti(self):
        W, H, s = self.W, self.H, self.scale
        for i in range(self.n):
            side = i % 3
            if side == 2:                                  # gentle rain from the top
                self._new(random.uniform(0, W), random.uniform(-H * 0.3, -10),
                          random.uniform(-40, 40) * s, random.uniform(20, 120) * s)
            else:                                          # cannons in the bottom corners
                x = -5 if side == 0 else W + 5
                ang = math.radians(random.uniform(55, 80))
                sp = random.uniform(0.75, 1.15) * math.sqrt(H * 2 * 1100 * s) * 0.95
                vx = math.cos(ang) * sp * (1 if side == 0 else -1)
                self._new(x, H + 5, vx, -math.sin(ang) * sp)

    def _burst(self):
        W, H, s = self.W, self.H, self.scale
        x, y = random.uniform(W * 0.15, W * 0.85), random.uniform(H * 0.12, H * 0.55)
        for _ in range(max(12, self.n // 4)):
            a = random.uniform(0, 6.283)
            sp = random.uniform(90, 330) * s
            self._new(x, y, math.cos(a) * sp, math.sin(a) * sp, shape="dot")

    # ── animation ─────────────────────────────────────────────────

    def _frame(self):
        if not self.alive:
            return
        now = time.perf_counter()
        t = now - self._t0
        dt = min(0.05, now - self._last)
        self._last = now
        if t >= self.DURATION:
            self.stop()
            return
        cv, s = self.cv, self.scale

        while self.bursts and t >= self.bursts[0]:
            self.bursts.pop(0)
            self._burst()

        # banner: pop in, then float up and shrink away at the end
        fam = theme.ui_family()
        pop = min(1.0, t / 0.22)
        ease = 1 - (1 - pop) ** 3
        over = 1.0 + 0.12 * math.sin(min(1.0, t / 0.35) * math.pi)
        out = max(0.0, (t - (self.DURATION - 0.35)) / 0.35)
        size = max(1, int((30 if self.big else 22) * s * ease * over * (1 - out)))
        cv.itemconfigure(self.b_title, font=(fam, -size, "bold"))
        cv.itemconfigure(self.b_sub, state="normal" if t > 0.18 and out < 0.6 else "hidden")
        cv.itemconfigure(self.pill, state="normal" if t > 0.08 and out < 0.6 else "hidden")
        if self.timer_item is not None:
            k = 0.5 + 0.5 * math.sin(t * 9)
            cv.itemconfigure(self.timer_item,
                             fill=theme.mix(pick(C["gold"]), pick(C["text"]), 0.55 * k * (1 - t / self.DURATION)))

        g = (1100 if self.style == "confetti" else 380) * s
        alive = []
        for p in self.parts:
            p["life"] += dt
            if p["shape"] == "dot":
                p["vx"] *= 0.93; p["vy"] = p["vy"] * 0.93 + g * dt
            else:
                p["vx"] *= 0.985; p["vy"] = min(p["vy"] * 0.985 + g * dt, 260 * s)
                p["vx"] += math.sin(t * 3 + p["flip"]) * 14 * s * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["rot"] += p["vr"] * dt
            p["flip"] += p["vf"] * dt
            if p["y"] > self.H + 40 or p["life"] > p["max"] or t > self.DURATION - 0.05:
                cv.delete(p["item"])
                continue
            alive.append(p)
            x, y, r = p["x"], p["y"], p["size"]
            if p["shape"] == "dot":
                r *= max(0.15, 1 - p["life"] / p["max"])
                cv.coords(p["item"], x - r / 2, y - r / 2, x + r / 2, y + r / 2)
            else:
                w, h = r / 2, r * 0.3 * abs(math.cos(p["flip"])) + 0.6
                c, sn = math.cos(p["rot"]), math.sin(p["rot"])
                cv.coords(p["item"],
                          x + (-w * c + h * sn), y + (-w * sn - h * c),
                          x + (w * c + h * sn), y + (w * sn - h * c),
                          x + (w * c - h * sn), y + (w * sn + h * c),
                          x + (-w * c - h * sn), y + (-w * sn + h * c))
        self.parts = alive
        cv.tag_raise(self.pill); cv.tag_raise(self.b_title); cv.tag_raise(self.b_sub)
        self._after = self.cv.after(16, self._frame)

    def stop(self):
        if not self.alive:
            return
        self.alive = False
        try:
            if self._after is not None:
                self.cv.after_cancel(self._after)
            if self._top is not None:
                self._top.destroy()
            else:
                self.cv.destroy()
        except tk.TclError:
            pass
        try:
            self.app._set_timer_color(self.app._state)
        except Exception:
            pass

"""Virtualised list of times: draws only the rows that are on screen.

A session with 50 000 solves costs the same as one with 50 - the old list
built three customtkinter widgets per solve, which is what made big
sessions slow to open and scroll.
"""
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk

from utils import fmt, display
from ui import theme
from ui.theme import C, pick

INF = float("inf")

COLUMN_TITLES = {"ao5": "ao5", "ao12": "ao12", "ao50": "ao50", "ao100": "ao100"}
ROW_HEIGHTS = {"compact": 24, "normal": 30, "comfy": 38}


# On Windows a <MouseWheel> event goes to the widget with keyboard focus (the
# main window, since the timer listens for SPACE), not the one under the
# pointer.  So one "all" binding routes wheel events to whichever list the
# pointer is over.
_LISTS = []
_WHEEL_ROOTS = set()


def _install_wheel(root):
    if str(root) in _WHEEL_ROOTS:
        return
    _WHEEL_ROOTS.add(str(root))

    def _route(e, delta=None):
        try:
            under = root.winfo_containing(e.x_root, e.y_root)
        except (KeyError, tk.TclError):
            return
        _LISTS[:] = [l for l in _LISTS if l.winfo_exists()]     # drop destroyed lists
        for lst in _LISTS:
            if under is not None and str(under) == str(lst.canvas):
                lst._on_wheel(e, delta)
                return

    root.bind_all("<MouseWheel>", _route, add="+")
    root.bind_all("<Button-4>", lambda e: _route(e, 120), add="+")
    root.bind_all("<Button-5>", lambda e: _route(e, -120), add="+")


class TimesList(ctk.CTkFrame):

    def __init__(self, master, app, on_click, on_context, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.app = app
        self.on_click = on_click
        self.on_context = on_context

        self.sb = ctk.CTkScrollbar(self, command=self._sb_cmd, width=12)
        self.sb.pack(side="right", fill="y", padx=(2, 0))
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, takefocus=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self._offset = 0.0         # pixels scrolled from the newest solve
        self._target = 0.0
        self._anim_id = None
        self._hover = None         # display index under the pointer

        c = self.canvas
        c.bind("<Configure>", lambda e: self.redraw())
        c.bind("<Motion>", self._on_motion)
        c.bind("<Leave>", self._on_leave)
        c.bind("<Button-1>", self._on_b1)
        c.bind("<Button-3>", self._on_b3)
        c.bind("<Button-2>", self._on_b3)          # macOS right click
        _install_wheel(self.winfo_toplevel())
        _LISTS.append(self)

    # ── data ──────────────────────────────────────────────────────

    def _times(self):
        return self.app.sm.get(self.app.cur)["times"]

    def _columns(self):
        return [c for c in self.app.cfg.g("times_list", "columns") if c in COLUMN_TITLES]

    def _scale(self):
        try:
            return ctk.ScalingTracker.get_widget_scaling(self)
        except Exception:
            return 1.0

    def _row_h(self):
        return int(ROW_HEIGHTS.get(self.app.cfg.g("times_list", "density"), 30) * self._scale())

    def _header_h(self):
        return int(24 * self._scale())

    def _max_offset(self):
        content = len(self._times()) * self._row_h()
        view = max(1, self.canvas.winfo_height() - self._header_h())
        return max(0, content - view)

    # ── scrolling ─────────────────────────────────────────────────

    def on_append(self):
        """A solve was added at the top: keep a scrolled-down view still."""
        if self._offset > 0.5:
            self._offset += self._row_h()
            self._target += self._row_h()
        self.redraw()

    def scroll_to_top(self):
        self._offset = self._target = 0.0
        self.redraw()

    def _set_offset(self, v, animate):
        v = max(0.0, min(float(self._max_offset()), v))
        self._target = v
        if not animate or not self.app.cfg.g("times_list", "smooth_scroll"):
            self._offset = v
            self.redraw()
            return
        if self._anim_id is None:
            self._animate()

    def _animate(self):
        d = self._target - self._offset
        if abs(d) < 0.6:
            self._offset = self._target
            self._anim_id = None
        else:
            self._offset += d * 0.32
            self._anim_id = self.after(12, self._animate)
        self.redraw()

    def _scroll_px(self, dy):
        self._set_offset(self._target + dy, animate=True)

    def _on_wheel(self, e, delta=None):
        delta = e.delta if delta is None else delta
        if abs(delta) >= 120:
            steps = -delta / 120.0                 # Windows: notches of 120
        else:
            steps = -delta                           # macOS: small deltas
        self._scroll_px(steps * 3 * self._row_h())

    def _sb_cmd(self, *args):
        if not args:
            return
        if args[0] == "moveto":
            total = len(self._times()) * self._row_h()
            self._set_offset(float(args[1]) * total, animate=False)
        elif args[0] == "scroll":
            n = int(args[1])
            if args[2] == "pages":
                step = self.canvas.winfo_height() - self._header_h() - self._row_h()
            else:
                step = self._row_h()
            self._scroll_px(n * step)

    # ── pointer ───────────────────────────────────────────────────

    def _index_at(self, y):
        """Entry index (into the session's times) at canvas y, or None."""
        if y < self._header_h():
            return None
        d = int((y - self._header_h() + self._offset) // self._row_h())
        n = len(self._times())
        if 0 <= d < n:
            return n - 1 - d
        return None

    def _on_motion(self, e):
        idx = self._index_at(e.y)
        if idx != self._hover:
            self._hover = idx
            self.canvas.configure(cursor="hand2" if idx is not None else "")
            self.redraw()

    def _on_leave(self, _e):
        if self._hover is not None:
            self._hover = None
            self.redraw()

    def _on_b1(self, e):
        idx = self._index_at(e.y)
        if idx is not None:
            self.on_click(idx)

    def _on_b3(self, e):
        idx = self._index_at(e.y)
        if idx is not None:
            self.on_context(e, idx)

    # ── drawing ───────────────────────────────────────────────────

    def redraw(self):
        """Repaint the visible rows. Cheap: ~one canvas item per visible cell."""
        c = self.canvas
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10 or h < 10:
            return
        times = self._times()
        n = len(times)
        self._offset = min(self._offset, float(self._max_offset()))
        self._target = min(self._target, float(self._max_offset()))

        s = self._scale()
        rh, hh = self._row_h(), self._header_h()
        dec = self.app.cfg.g("timer", "decimals")
        cols = self._columns()
        st = self.app.stats
        acc = theme.accent(self.app.cfg)
        fam = theme.ui_family()
        mono = self.app.cfg.g("times_list", "mono_digits")
        tfam = theme.mono_family() if mono else fam
        fs = max(8, int(11 * s)) if rh < 28 * s else max(9, int(12 * s))

        bg = pick(C["panel"])
        c.configure(bg=bg)
        c.delete("all")

        # column x positions: number | time | extra columns (right aligned)
        num_font = tkfont.Font(family=fam, size=fs - 1)
        num_w = max(int(30 * s), num_font.measure(f"{max(n, 9)}.") + int(6 * s))
        col_w = int(64 * s)
        right = w - int(8 * s)
        col_x = {}
        for k in reversed(cols):
            col_x[k] = right
            right -= col_w
        time_x = num_w + int(10 * s)

        if n == 0:
            c.create_text(w // 2, hh + int(40 * s), text="Brak czasów\nprzytrzymaj SPACJĘ",
                          fill=pick(C["muted"]), font=(fam, fs), justify="center")
        first = int(self._offset // rh)
        last = min(n, first + (h - hh) // rh + 2)
        y0 = hh - (self._offset - first * rh)
        best_idx = st.best_idx if self.app.cfg.g("times_list", "highlight_pb") else None
        row_bg = (pick(C["row"]), pick(C["row_alt"]))
        hover_bg = pick(theme.tint(acc, "panel", 0.16))
        txt, muted, bad, gold = pick(C["text"]), pick(C["muted"]), pick(C["bad"]), pick(C["gold"])
        pad = int(3 * s)

        for d in range(first, last):
            i = n - 1 - d
            y = y0 + (d - first) * rh
            e = times[i]
            fill = hover_bg if i == self._hover else row_bg[d % 2]
            c.create_rectangle(pad, y + 1, w - pad, y + rh - 1, fill=fill, width=0)
            cy = y + rh // 2
            c.create_text(num_w, cy, text=f"{i + 1}.", anchor="e", fill=muted, font=num_font)
            pen = e.get("penalty")
            if pen in ("DNF", "DNS"):
                tcol, ttxt = bad, pen
                if self.app.cfg.g("times_list", "show_raw_on_dnf"):
                    ttxt = f"{pen} ({fmt(e['time'], dec)})"
            else:
                ttxt = display(e, dec) + ("+" if pen == "+2" else "")
                tcol = gold if i == best_idx else txt
            c.create_text(time_x, cy, text=ttxt, anchor="w", fill=tcol,
                          font=(tfam, fs + 1, "bold"))
            if e.get("note"):
                c.create_text(time_x - int(4 * s), cy, text="•", anchor="e",
                              fill=pick(acc), font=(fam, fs))
            for k in cols:
                v = st.at(int(k[2:]), i)
                if v is None:
                    vt = "—"
                elif v == INF:
                    vt = "DNF"
                else:
                    vt = fmt(v, min(dec, 2))
                c.create_text(col_x[k], cy, text=vt, anchor="e", fill=muted, font=(tfam, fs))

        # header drawn last so rows scroll underneath it
        c.create_rectangle(0, 0, w, hh, fill=bg, width=0)
        c.create_line(pad, hh - 1, w - pad, hh - 1, fill=pick(C["border"]))
        hf = (fam, max(8, fs - 2), "bold")
        c.create_text(num_w, hh // 2, text="#", anchor="e", fill=muted, font=hf)
        c.create_text(time_x, hh // 2, text="czas", anchor="w", fill=muted, font=hf)
        for k in cols:
            c.create_text(col_x[k], hh // 2, text=COLUMN_TITLES[k], anchor="e", fill=muted, font=hf)

        total = max(1, n * rh)
        view = h - hh
        if total <= view:
            self.sb.set(0.0, 1.0)
        else:
            self.sb.set(self._offset / total, (self._offset + view) / total)

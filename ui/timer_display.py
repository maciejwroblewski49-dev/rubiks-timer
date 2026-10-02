"""The big timer digits, drawn on a canvas with every digit in a fixed-width
cell ("tabular" figures), so a modern proportional font like Poppins can be
used without the number wobbling left and right while the time runs.
"""
import tkinter as tk
import tkinter.font as tkfont

from ui import theme
from ui.theme import pick

_NARROW = set(".:,")


class TimerDisplay(tk.Canvas):

    def __init__(self, master, textvariable, bg):
        super().__init__(master, highlightthickness=0, bd=0, bg=bg, takefocus=0)
        self._var = textvariable
        self._color = "#ffffff"
        self._family, self._weight = theme.spec("bold")
        self._px = 100
        self._font = tkfont.Font(family=self._family, size=-self._px, weight=self._weight)
        self._cell = None
        self.tabular = False        # fixed-width digits only while the time runs
        self._var.trace_add("write", lambda *a: self.redraw())
        self.bind("<Configure>", lambda e: self.redraw())

    # ── appearance ────────────────────────────────────────────────

    def set_color(self, color):
        self._color = color
        self.itemconfigure("timer", fill=pick(color))

    def set_bg(self, color):
        self.configure(bg=pick(color))

    def set_font(self, family=None, px=None):
        if family is not None:
            self._family, self._weight = theme.spec("bold", family)
        if px is not None:
            self._px = max(8, int(px))
        self._font.configure(family=self._family, size=-self._px, weight=self._weight)
        self._cell = None
        self.redraw()

    @property
    def px(self):
        return self._px

    def set_tabular(self, on):
        if bool(on) != self.tabular:
            self.tabular = bool(on)
            self.redraw()

    def _digit_cell(self):
        if self._cell is None:
            self._cell = max(self._font.measure(d) for d in "0123456789")
        return self._cell

    def text_width(self, text, px=None):
        """Width of `text` laid out in tabular cells (at px, default current)."""
        if px is not None and px != self._px:
            f = tkfont.Font(family=self._family, size=-int(px), weight=self._weight)
            cell = max(f.measure(d) for d in "0123456789")
            return sum(cell if ch.isdigit() else f.measure(ch) for ch in text)
        cell = self._digit_cell()
        return sum(cell if ch.isdigit() else self._font.measure(ch) for ch in text)

    # ── drawing ───────────────────────────────────────────────────

    def redraw(self):
        self.delete("timer")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return
        text = self._var.get()
        cy = h / 2
        col = pick(self._color)
        if not self.tabular:
            # static result: one text item, the font's own spacing and kerning
            self.create_text(w / 2, cy, text=text, fill=col, font=self._font,
                             anchor="center", tags=("timer",))
            self.tag_lower("timer")
            return
        cell = self._digit_cell()
        widths = [cell if ch.isdigit() else self._font.measure(ch) for ch in text]
        x = (w - sum(widths)) / 2
        for ch, cw in zip(text, widths):
            if ch != " ":
                self.create_text(x + cw / 2, cy, text=ch, fill=col, font=self._font,
                                 anchor="center", tags=("timer",))
            x += cw
        self.tag_lower("timer")

    def digits_bbox(self):
        return self.bbox("timer")

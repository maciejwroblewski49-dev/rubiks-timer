"""Dialog shown when you left-click a time in the list: big time, scramble, 2D cube net, penalty toggles, delete, notes."""
import tkinter as tk
import customtkinter as ctk
from datetime import datetime

from utils import _bring_to_front, display
from cube_sim import _make_viz_state, _viz_net_dims


class TimeDetailDialog(ctk.CTkToplevel):

    def __init__(self, parent_app, idx):
        super().__init__(parent_app)
        self._app = parent_app
        self._idx = idx

        entry = self._entry()
        if entry is None:
            self.destroy(); return

        scramble = entry.get("scramble", "")
        puzzle   = entry.get("puzzle", "3x3")
        self._viz_state = _make_viz_state(puzzle, scramble)
        has_viz  = self._viz_state is not None

        self.geometry("460x" + ("640" if has_viz else "440"))
        self.resizable(False, True)
        self.minsize(360, 320)
        self.title(f"Solv #{idx + 1}")
        self.protocol("WM_DELETE_WINDOW", self._save_and_close)

        self._build(entry, scramble, has_viz)
        _bring_to_front(self)

    # ── helpers ───────────────────────────────────────────────────

    def _entry(self):
        times = self._app.sm.get(self._app.cur)["times"]
        return times[self._idx] if self._idx < len(times) else None

    # ── layout ────────────────────────────────────────────────────

    def _build(self, entry, scramble, has_viz):
        dec     = self._app.cfg.g("timer", "decimals")
        penalty = entry.get("penalty")

        t_color = "#FF4444" if penalty in ("+2", "DNF", "DNS") else "#FFFFFF"

        # ── big time ──
        self._time_lbl = ctk.CTkLabel(
            self, text=display(entry, dec),
            font=ctk.CTkFont(size=52, weight="bold"), text_color=t_color)
        self._time_lbl.pack(pady=(18, 0))

        ctk.CTkLabel(self, text=f"Solv #{self._idx + 1}",
                     font=ctk.CTkFont(size=11),
                     text_color="gray50").pack()

        # ── date ──
        raw = entry.get("date", "")
        if raw:
            try:
                dt = datetime.fromisoformat(raw)
                date_str = dt.strftime("%d.%m.%Y  %H:%M:%S")
            except Exception:
                date_str = raw
            ctk.CTkLabel(self, text=f"📅  {date_str}",
                         font=ctk.CTkFont(size=12),
                         text_color="gray55").pack(pady=(6, 0))

        # ── scramble ──
        if scramble:
            ctk.CTkFrame(self, height=1, fg_color="gray28").pack(
                fill="x", padx=16, pady=(12, 8))
            ctk.CTkLabel(self, text="Scramble", font=ctk.CTkFont(size=10),
                         text_color="gray50", anchor="w").pack(
                fill="x", padx=18, pady=(0, 2))
            ctk.CTkLabel(self, text=scramble,
                         font=ctk.CTkFont(size=11, family="Consolas"),
                         wraplength=420, justify="center",
                         text_color="#CCCCCC").pack(padx=16, pady=(0, 6))

        # ── 2D cube visualization ──
        if has_viz:
            vf = ctk.CTkFrame(self, fg_color=("#cccccc", "#16162a"), corner_radius=8)
            vf.pack(fill="both", expand=True, padx=12, pady=(0, 8))

            self._vc = tk.Canvas(vf, bg="#16162a", highlightthickness=0)
            self._vc.pack(fill="both", expand=True, padx=4, pady=4)

            def _draw(event=None, _st=self._viz_state):
                c = self._vc
                c.update_idletasks()
                w = c.winfo_width(); h = c.winfo_height()
                if w < 30 or h < 30 or _st is None: return
                nc, nr = _viz_net_dims(_st)
                cell = min(w // (nc+1), h // (nr+1))
                if cell < 3: return
                x0 = (w - nc * cell) // 2
                y0 = (h - nr * cell) // 2
                c.delete("all")
                _st.draw_net(c, x0, y0, cell)

            self._vc.bind("<Configure>", lambda e: _draw())
            self.after(120, _draw)

        # ── separator ──
        ctk.CTkFrame(self, height=1, fg_color="gray28").pack(
            fill="x", padx=16, pady=(4, 10))

        # ── penalty toggles ──
        pen_row = ctk.CTkFrame(self, fg_color="transparent")
        pen_row.pack(pady=(0, 8))
        self._pen_btns = {}
        for p in ["+2", "DNF", "DNS"]:
            b = ctk.CTkButton(
                pen_row, text=p, width=68, height=30,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="gray22", hover_color="gray30", corner_radius=8,
                command=lambda x=p: self._toggle_pen(x))
            b.pack(side="left", padx=4)
            self._pen_btns[p] = b
        ctk.CTkFrame(pen_row, width=1, height=26, fg_color="gray35").pack(
            side="left", padx=8)
        ctk.CTkButton(pen_row, text="🗑 Usuń", width=80, height=30,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      fg_color="#7a1010", hover_color="#5a0a0a", corner_radius=8,
                      command=self._delete).pack(side="left", padx=4)
        self._refresh_pen_btns(penalty)

        # ── notes ──
        ctk.CTkFrame(self, height=1, fg_color="gray28").pack(fill="x", padx=16, pady=(4, 6))
        ctk.CTkLabel(self, text="Notatka", font=ctk.CTkFont(size=10),
                     text_color="gray50", anchor="w").pack(fill="x", padx=18, pady=(0, 2))
        self._note_box = ctk.CTkTextbox(self, height=64, font=ctk.CTkFont(size=12))
        self._note_box.pack(fill="x", padx=16, pady=(0, 6))
        self._note_box.insert("1.0", entry.get("note", ""))

        # ── action buttons ──
        act_row = ctk.CTkFrame(self, fg_color="transparent")
        act_row.pack(pady=(0, 16))
        ctk.CTkButton(act_row, text="Zamknij", width=110, height=30,
                      fg_color="gray25", hover_color="gray35",
                      command=self._save_and_close).pack(side="left", padx=6)

    # ── penalty ───────────────────────────────────────────────────

    def _refresh_pen_btns(self, active):
        for p, b in self._pen_btns.items():
            if p == active:
                b.configure(fg_color=("#1a5fa0", "#1f6aa5"),
                            hover_color=("#155090", "#1a5a90"))
            else:
                b.configure(fg_color="gray22", hover_color="gray30")

    def _toggle_pen(self, pen):
        entry = self._entry()
        if entry is None: return
        self._app._set_pen(self._idx, pen)
        entry = self._entry()
        if entry is None: return
        dec     = self._app.cfg.g("timer", "decimals")
        penalty = entry.get("penalty")
        t_color = "#FF4444" if penalty in ("+2", "DNF", "DNS") else "#FFFFFF"
        self._time_lbl.configure(text=display(entry, dec), text_color=t_color)
        self._refresh_pen_btns(penalty)
        if self._app._tools_win and self._app._tools_win.winfo_exists():
            self._app._tools_win.refresh_after_solve()

    # ── notes ─────────────────────────────────────────────────────

    def _save_note(self):
        if not hasattr(self, "_note_box"): return
        entry = self._entry()
        if entry is None: return
        note = self._note_box.get("1.0", "end").rstrip("\n")
        if entry.get("note", "") != note:
            entry = dict(entry)
            entry["note"] = note
            self._app.sm.update(self._app.cur, self._idx, entry)

    def _save_and_close(self):
        self._save_note()
        self.destroy()

    # ── delete ────────────────────────────────────────────────────

    def _delete(self):
        self._app._del_time(self._idx)
        # _del_time closes this dialog via _app._detail_win

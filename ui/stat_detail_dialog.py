"""Dialog shown when you click a stat (Ao5/Ao12/Ao100/mean/best, or the "PB" under an average): the solves that make up that statistic.

The rows live in one tk.Text widget instead of a frame per solve, so even
"mean of 20 000 solves" opens instantly.
"""
import tkinter as tk
import customtkinter as ctk

from utils import _bring_to_front, fmt, display, effective
from stats import trim_count
from ui import theme
from ui.theme import C, pick

INF = float("inf")


class StatDetailDialog(ctk.CTkToplevel):

    def __init__(self, parent_app, key):
        super().__init__(parent_app)
        self._app = parent_app
        times = parent_app.sm.get(parent_app.cur)["times"]
        dec   = parent_app.cfg.g("timer", "decimals")

        rows, title, val_str = self._compute(key, times, dec)
        if rows is None:
            self.destroy(); return

        self.title(f"{title} — {val_str}")
        h = max(260, min(640, 170 + len(rows) * 46))
        self.geometry(f"560x{h}")
        self.minsize(420, 220)
        self.resizable(True, True)
        self.configure(fg_color=C["bg"])
        self._build(title, val_str, rows, dec)
        _bring_to_front(self)

    # ── data builders ─────────────────────────────────────────────

    def _compute(self, key, times, dec):
        st = self._app.stats
        if key == "mean":  return self._mean_data(times, dec)
        if key == "best":  return self._best_data(times, dec)
        if key.startswith("_best_"):
            n = int(key[6:])
            v, end = st.best_average(n)
            if end is None:
                return None, "Najlepsze", "—"
            return self._ao_data(n, times, dec, "Najlepsze " + ("Mo3" if n == 3 else f"Ao{n}"), end=end)
        if key.startswith("_cao_"):
            n = int(key[5:])
        elif key.startswith("ao"):
            n = int(key[2:])
        else:
            return None, key, "—"
        return self._ao_data(n, times, dec, "Mo3" if n == 3 else f"Ao{n}")

    def _ao_data(self, n, times, dec, label, end=None):
        if len(times) < n: return None, label, "—"
        end = len(times) - 1 if end is None else end
        offset = end - n + 1
        sub    = times[offset:end + 1]
        effs   = [effective(e) for e in sub]
        order  = sorted(range(n), key=lambda i: effs[i])
        t      = trim_count(n, self._app.cfg.g("stats", "trim_mode"))
        low, high = set(order[:t]), set(order[n - t:]) if t else set()
        kept = [effs[i] for i in order[t:n - t]] if t else effs
        if any(v == INF for v in kept):
            val_str = "DNF"
        elif kept:
            val_str = fmt(sum(kept) / len(kept), dec)
        else:
            val_str = "—"
        rows = []
        for i, e in enumerate(sub):
            role = "best" if i in low else ("worst" if i in high else "normal")
            rows.append((offset + i, e, role))
        return rows, label, val_str

    def _mean_data(self, times, dec):
        valid = [(i, e) for i, e in enumerate(times) if effective(e) != INF]
        if not valid: return None, "Średnia sesji", "—"
        vals = [effective(e) for _, e in valid]
        val_str = fmt(sum(vals) / len(vals), dec)
        return [(i, e, "normal") for i, e in valid], "Średnia sesji", val_str

    def _best_data(self, times, dec):
        st = self._app.stats
        if st.best_idx is None: return None, "Najlepszy", "—"
        e = times[st.best_idx]
        return [(st.best_idx, e, "best")], "Najlepszy", display(e, dec)

    # ── layout ────────────────────────────────────────────────────

    def _build(self, title, val_str, rows, dec):
        ctk.CTkLabel(self, text=title.upper(), text_color=C["muted"],
                     font=theme.font(12, "bold")).pack(pady=(16, 0))
        ctk.CTkLabel(self, text=val_str, text_color=C["text"],
                     font=theme.font(36, "bold")).pack()
        ctk.CTkLabel(self, text=f"{len(rows)} solvów  •  kliknij wiersz, aby zobaczyć szczegóły"
                               + ("  •  (czasy w nawiasach są odrzucone)" if any(r[2] != "normal" for r in rows) else ""),
                     font=theme.font(11), text_color=C["muted"]).pack(pady=(0, 8))

        box = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=12,
                           border_width=1, border_color=C["border"])
        box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        fam, mono = theme.ui_family(), theme.mono_family()
        txt = tk.Text(box, wrap="word", bd=0, highlightthickness=0, cursor="hand2",
                      bg=pick(C["panel"]), fg=pick(C["text"]), padx=10, pady=8,
                      font=(fam, 11), spacing1=4, spacing3=4)
        sb = ctk.CTkScrollbar(box, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=6)
        txt.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)

        txt.tag_configure("num", foreground=pick(C["muted"]), font=(fam, 10))
        txt.tag_configure("t", font=theme.tkf(13, "bold"))
        txt.tag_configure("best", foreground=pick(C["good"]))
        txt.tag_configure("worst", foreground=pick(C["bad"]))
        txt.tag_configure("scr", foreground=pick(C["muted"]), font=(mono, 9),
                          lmargin1=12, lmargin2=12)
        txt.tag_configure("hover", background=pick(C["panel_alt"]))

        self._line_to_idx = {}
        line = 1
        for gidx, entry, role in rows:
            disp = display(entry, dec)
            if role != "normal":
                disp = f"({disp})"
            txt.insert("end", f"#{gidx + 1}   ", ("num",))
            txt.insert("end", disp, ("t", role))
            if entry.get("note"):
                txt.insert("end", f"   📝 {entry['note']}", ("num",))
            txt.insert("end", "\n")
            scr = entry.get("scramble", "")
            txt.insert("end", (scr or "—") + "\n", ("scr",))
            self._line_to_idx[line] = gidx
            self._line_to_idx[line + 1] = gidx
            line += 2
        txt.configure(state="disabled")

        def _idx_at(e):
            ln = int(txt.index(f"@{e.x},{e.y}").split(".")[0])
            return ln, self._line_to_idx.get(ln)

        def _click(e):
            _, i = _idx_at(e)
            if i is not None:
                self._app._show_detail(i)

        def _motion(e):
            ln, i = _idx_at(e)
            txt.tag_remove("hover", "1.0", "end")
            if i is not None:
                first = ln if ln % 2 == 1 else ln - 1
                txt.tag_add("hover", f"{first}.0", f"{first + 2}.0")

        txt.bind("<Button-1>", _click)
        txt.bind("<Motion>", _motion)
        txt.bind("<Leave>", lambda e: txt.tag_remove("hover", "1.0", "end"))

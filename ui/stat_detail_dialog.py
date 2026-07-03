"""Dialog shown when you click a stat (Ao5/Ao12/Ao100/mean/best): the list of solves that make up that statistic."""
import customtkinter as ctk

from utils import _bring_to_front, fmt, display, effective


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
        h = max(240, min(640, 140 + len(rows) * 64))
        self.geometry(f"530x{h}")
        self.minsize(400, 200)
        self.resizable(True, True)
        self._build(title, val_str, rows, dec)
        _bring_to_front(self)

    # ── data builders ─────────────────────────────────────────────

    def _compute(self, key, times, dec):
        if key == "ao5":   return self._ao_data(5,   times, dec, "Ao5")
        if key == "ao12":  return self._ao_data(12,  times, dec, "Ao12")
        if key == "ao100": return self._ao_data(100, times, dec, "Ao100")
        if key == "mean":  return self._mean_data(times, dec)
        if key == "best":  return self._best_data(times, dec)
        if key.startswith("_cao_"):
            n = int(key[5:])
            return self._ao_data(n, times, dec, f"Ao{n}")
        return None, key, "—"

    def _ao_data(self, n, times, dec, label):
        if len(times) < n: return None, label, "—"
        sub    = times[-n:]
        offset = len(times) - n
        effs   = [effective(e) for e in sub]
        order  = sorted(range(n), key=lambda i: effs[i])
        best_i, worst_i = order[0], order[-1]
        mid_vals = [effs[i] for i in order[1:-1]]
        if any(v == float("inf") for v in mid_vals):
            val_str = "DNF"
        elif mid_vals:
            val_str = fmt(sum(mid_vals) / len(mid_vals), dec)
        else:
            val_str = "—"
        rows = []
        for i, e in enumerate(sub):
            role = "best" if i == best_i else ("worst" if i == worst_i else "normal")
            rows.append((offset + i, e, role))
        return rows, label, val_str

    def _mean_data(self, times, dec):
        valid = [(i, e) for i, e in enumerate(times) if effective(e) != float("inf")]
        if not valid: return None, "Średnia sesji", "—"
        vals = [effective(e) for _, e in valid]
        val_str = fmt(sum(vals) / len(vals), dec)
        return [(i, e, "normal") for i, e in valid], "Średnia sesji", val_str

    def _best_data(self, times, dec):
        valid = [(i, e) for i, e in enumerate(times) if effective(e) != float("inf")]
        if not valid: return None, "Najlepszy", "—"
        best_i, best_e = min(valid, key=lambda x: effective(x[1]))
        return [(best_i, best_e, "best")], "Najlepszy", display(best_e, dec)

    # ── layout ────────────────────────────────────────────────────

    def _build(self, title, val_str, rows, dec):
        ctk.CTkLabel(self, text=f"{title}  =  {val_str}",
                     font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(16, 2))
        ctk.CTkLabel(self, text=f"{len(rows)} solvów  •  kliknij wiersz aby zobaczyć szczegóły",
                     font=ctk.CTkFont(size=11), text_color="gray50").pack()
        ctk.CTkFrame(self, height=1, fg_color="gray28").pack(fill="x", padx=16, pady=8)

        sf = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for row_num, (gidx, entry, role) in enumerate(rows):
            bg = ("gray80", "gray20") if row_num % 2 == 0 else ("gray84", "gray17")
            rf = ctk.CTkFrame(sf, fg_color=bg, corner_radius=6, cursor="hand2")
            rf.pack(fill="x", padx=2, pady=2)
            rf.grid_columnconfigure(1, weight=1)

            num_lbl = ctk.CTkLabel(rf, text=f"#{gidx+1}", width=38,
                                   font=ctk.CTkFont(size=11), text_color="gray55")
            num_lbl.grid(row=0, column=0, padx=(8, 4), pady=(6, 2), sticky="w")

            if role == "best":    t_col = "#4CAF50"
            elif role == "worst": t_col = "#E57373"
            else:                 t_col = "#FFFFFF"

            disp = display(entry, dec)
            if role in ("best", "worst"):
                disp = f"({disp})"

            t_lbl = ctk.CTkLabel(rf, text=disp,
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  text_color=t_col)
            t_lbl.grid(row=0, column=1, padx=4, pady=(6, 2), sticky="w")

            if role == "best":
                badge = ctk.CTkLabel(rf, text="BEST", width=46, height=18,
                                     font=ctk.CTkFont(size=9, weight="bold"),
                                     fg_color="#1a5a2a", corner_radius=4,
                                     text_color="#4CAF50")
                badge.grid(row=0, column=2, padx=(0, 8), pady=(6, 2))
            elif role == "worst":
                badge = ctk.CTkLabel(rf, text="WORST", width=50, height=18,
                                     font=ctk.CTkFont(size=9, weight="bold"),
                                     fg_color="#4a1818", corner_radius=4,
                                     text_color="#E57373")
                badge.grid(row=0, column=2, padx=(0, 8), pady=(6, 2))
            else:
                badge = None

            scr = entry.get("scramble", "")
            scr_lbl = ctk.CTkLabel(rf, text=scr,
                                    font=ctk.CTkFont(size=10, family="Consolas"),
                                    text_color="gray50", anchor="w", wraplength=440)
            scr_lbl.grid(row=1, column=0, columnspan=3, padx=8, pady=(0, 6), sticky="w")

            click_targets = [rf, num_lbl, t_lbl, scr_lbl]
            if badge: click_targets.append(badge)
            for w in click_targets:
                w.bind("<Button-1>", lambda e, i=gidx: self._open_detail(i))
            rf.bind("<Enter>", lambda e, f=rf: f.configure(fg_color=("gray75", "gray25")))
            rf.bind("<Leave>", lambda e, f=rf, b=bg: f.configure(fg_color=b))

    def _open_detail(self, idx):
        self._app._show_detail(idx)

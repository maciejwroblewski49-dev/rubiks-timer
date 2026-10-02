"""Tools window: scramble chart, histogram, full stats table, cube visualization tab, practice metronome."""
import math, threading, time
import tkinter as tk
import customtkinter as ctk

from utils import _bring_to_front, fmt, display, effective, _HAS_WINSOUND, _winsound
from cube_sim import _make_viz_state, _viz_net_dims


_HAS_MPL = None                     # None = not tried yet
Figure = None
FigureCanvasTkAgg = None
def _load_mpl():
    global _HAS_MPL, Figure, FigureCanvasTkAgg
    if _HAS_MPL is not None:
        return _HAS_MPL
    try:
        from matplotlib.figure import Figure as _F
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as _C
        Figure = _F; FigureCanvasTkAgg = _C; _HAS_MPL = True
    except Exception:
        _HAS_MPL = False
    return _HAS_MPL


class ToolsWindow(ctk.CTkToplevel):

    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.title("Narzędzia")
        self.geometry("780x560")
        self.minsize(640, 480)
        self._app = parent_app

        # metronome state
        self._metro_running  = False
        self._metro_stop     = threading.Event()
        self._metro_interval = 20
        self._metro_next     = 0.0

        self._viz_resize_id  = None
        self._chart_resize_id = None
        self._hist_resize_id  = None
        self._refresh_id      = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self.lift()
        self.focus_set()

    # ── build ─────────────────────────────────────────────────────

    def _build(self):
        tabs = ctk.CTkTabview(self, command=self._refresh_current)
        tabs.pack(fill="both", expand=True, padx=8, pady=8)
        self._tabs = tabs
        for t in ["📈  Wykres", "📊  Histogram", "🔢  Statystyki",
                  "🎲  Wizualizacja", "🎵  Metronom"]:
            tabs.add(t)
        self._build_chart(tabs.tab("📈  Wykres"))
        self._build_histogram(tabs.tab("📊  Histogram"))
        self._build_stats(tabs.tab("🔢  Statystyki"))
        self._build_viz(tabs.tab("🎲  Wizualizacja"))
        self._build_metro(tabs.tab("🎵  Metronom"))

    # ── shared helpers ────────────────────────────────────────────

    def _times(self):
        return self._app.sm.get(self._app.cur)["times"]

    def _stats(self):
        st = self._app.stats
        if st.count != len(self._times()):
            st.load(self._times())
        return st

    def _valid(self):
        return [v for v in self._stats().effs if v != float("inf")]

    def _ao_n(self, n):
        return self._stats().current(n)

    def _best_ao_n(self, n):
        return self._stats().best_average(n)[0]

    def _fmts(self, v):
        dec = self._app.cfg.g("timer", "decimals")
        if v is None: return "—"
        if v == float("inf"): return "DNF"
        return fmt(v, dec)

    # ── matplotlib helpers ────────────────────────────────────────

    def _dark_axes(self, ax):
        ax.set_facecolor("#16162a")
        ax.tick_params(colors="#888899", labelsize=8)
        ax.xaxis.label.set_color("#888899")
        ax.yaxis.label.set_color("#888899")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333355")
        ax.grid(True, color="#222244", linewidth=0.6)

    def _make_fig(self, master):
        fig = Figure(dpi=96, facecolor="#16162a")
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return fig, canvas

    # ── Tab: Wykres ───────────────────────────────────────────────

    def _build_chart(self, tab):
        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.pack(fill="x", padx=6, pady=(6, 2))
        ctk.CTkButton(bar, text="Odśwież", width=88, height=28,
                      command=self.refresh_chart).pack(side="right")

        if not _load_mpl():
            ctk.CTkLabel(tab,
                         text="Brak matplotlib.\nZainstaluj: py -m pip install matplotlib",
                         font=ctk.CTkFont(size=13), text_color="gray55").pack(expand=True)
            return

        self._chart_fig, self._chart_cv = self._make_fig(tab)
        self._chart_ax = self._chart_fig.add_subplot(111)

        def _on_resize(e):
            if self._chart_resize_id:
                self.after_cancel(self._chart_resize_id)
            self._chart_resize_id = self.after(80, self._do_chart_resize,
                                                e.width, e.height)
        self._chart_cv.get_tk_widget().bind("<Configure>", _on_resize)
        self.after(150, self.refresh_chart)

    def _do_chart_resize(self, w, h):
        if w > 20 and h > 20:
            self._chart_fig.set_size_inches(w / 96, h / 96)
            self.refresh_chart()

    def refresh_chart(self):
        if not _load_mpl() or not hasattr(self, "_chart_ax"):
            return
        ax = self._chart_ax
        ax.clear()
        self._dark_axes(ax)

        times = self._times()
        dec   = self._app.cfg.g("timer", "decimals")

        if not times:
            ax.text(0.5, 0.5, "Brak czasów w sesji",
                    ha="center", va="center", color="#666677",
                    transform=ax.transAxes, fontsize=13)
            self._chart_fig.tight_layout(pad=1.2)
            self._chart_cv.draw_idle()
            return

        xs, ys, xs_bad = [], [], []
        for i, e in enumerate(times):
            eff = effective(e)
            if eff == float("inf"):
                xs_bad.append(i + 1)
            else:
                xs.append(i + 1); ys.append(eff)

        if ys:
            many = len(ys) > 400       # big sessions: thin line, tiny dots
            ax.plot(xs, ys, color="#3dbb77", lw=0.6 if many else 1.2,
                    alpha=0.5 if many else 0.75, zorder=2)
            ax.scatter(xs, ys, color="#3dbb77", s=2 if many else 12, zorder=3)

        top_y = max(ys) * 1.08 if ys else 60
        if xs_bad:
            ax.scatter(xs_bad, [top_y] * len(xs_bad),
                       color="#ff5555", s=22, marker="x", zorder=4, label="DNF/DNS")

        # rolling averages straight from the stats engine (cached, O(1) per
        # point after the first draw) instead of re-sorting every window
        st = self._stats()
        ao5_pts, ao12_pts = [], []
        for n, pts in ((5, ao5_pts), (12, ao12_pts)):
            for i, v in enumerate(st.rolling(n)):
                if v is not None and v != float("inf"):
                    pts.append((i + 1, v))
        if ao5_pts:
            ax.plot([p[0] for p in ao5_pts], [p[1] for p in ao5_pts],
                    color="#ffaa33", lw=1.6, label="Ao5", zorder=5)
        if ao12_pts:
            ax.plot([p[0] for p in ao12_pts], [p[1] for p in ao12_pts],
                    color="#5588ff", lw=1.6, label="Ao12", zorder=5)

        ax.set_xlabel("Numer solva", fontsize=9)
        ax.set_ylabel("Czas (s)", fontsize=9)
        if xs_bad or ao5_pts or ao12_pts:
            leg = ax.legend(fontsize=8, facecolor="#16162a",
                            edgecolor="#333355", labelcolor="#aaaacc")

        self._chart_fig.tight_layout(pad=1.2)
        self._chart_cv.draw_idle()

    # ── Tab: Histogram ────────────────────────────────────────────

    def _build_histogram(self, tab):
        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.pack(fill="x", padx=6, pady=(6, 2))
        ctk.CTkButton(bar, text="Odśwież", width=88, height=28,
                      command=self.refresh_histogram).pack(side="right")

        if not _load_mpl():
            ctk.CTkLabel(tab,
                         text="Brak matplotlib.\nZainstaluj: py -m pip install matplotlib",
                         font=ctk.CTkFont(size=13), text_color="gray55").pack(expand=True)
            return

        self._hist_fig, self._hist_cv = self._make_fig(tab)
        self._hist_ax = self._hist_fig.add_subplot(111)

        def _on_resize(e):
            if self._hist_resize_id:
                self.after_cancel(self._hist_resize_id)
            self._hist_resize_id = self.after(80, self._do_hist_resize,
                                               e.width, e.height)
        self._hist_cv.get_tk_widget().bind("<Configure>", _on_resize)
        self.after(150, self.refresh_histogram)

    def _do_hist_resize(self, w, h):
        if w > 20 and h > 20:
            self._hist_fig.set_size_inches(w / 96, h / 96)
            self.refresh_histogram()

    def refresh_histogram(self):
        if not _load_mpl() or not hasattr(self, "_hist_ax"):
            return
        ax = self._hist_ax
        ax.clear()
        self._dark_axes(ax)

        vals = self._valid()
        if len(vals) < 2:
            ax.text(0.5, 0.5, "Za mało czasów (potrzeba ≥ 2)",
                    ha="center", va="center", color="#666677",
                    transform=ax.transAxes, fontsize=13)
            self._hist_fig.tight_layout(pad=1.2)
            self._hist_cv.draw_idle()
            return

        bins = min(20, max(5, len(vals) // 3))
        ax.hist(vals, bins=bins, color="#5588ff", edgecolor="#16162a", alpha=0.85)
        ax.set_xlabel("Czas (s)", fontsize=9)
        ax.set_ylabel("Liczba solvów", fontsize=9)
        ax.grid(True, color="#222244", linewidth=0.6, axis="y")
        self._hist_fig.tight_layout(pad=1.2)
        self._hist_cv.draw_idle()

    # ── Tab: Statystyki ───────────────────────────────────────────

    def _build_stats(self, tab):
        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.pack(fill="x", padx=6, pady=(6, 2))
        ctk.CTkButton(bar, text="Odśwież", width=88, height=28,
                      command=self.refresh_stats).pack(side="left", padx=(0, 8))
        ctk.CTkButton(bar, text="📋 Kopiuj", width=100, height=28,
                      command=self._copy_stats).pack(side="left")

        self._stats_sf = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self._stats_sf.pack(fill="both", expand=True, padx=6, pady=(2, 6))
        self._stats_sf.grid_columnconfigure(0, weight=1)
        self._stats_data = []
        self.refresh_stats()

    def refresh_stats(self):
        for w in self._stats_sf.winfo_children():
            w.destroy()

        times = self._times()
        valid = self._valid()
        dec   = self._app.cfg.g("timer", "decimals")

        st    = self._stats()
        dnf_n = st.dnf_count
        median_v = st.median()
        std_v    = st.std
        rows = [
            ("── Ogólne ──────────────────────────────",  None),
            ("Wszystkich solvów",   str(len(times))),
            ("Valid (bez DNF/DNS)", str(len(valid))),
            ("DNF / DNS",           str(dnf_n)),
            ("── Czasy ───────────────────────────────",  None),
            ("Najlepszy",           self._fmts(st.best)),
            ("Najgorszy",           self._fmts(st.worst)),
            ("Średnia sesji",       self._fmts(st.mean)),
            ("Mediana",             self._fmts(median_v)),
            ("Odch. std.",          self._fmts(std_v)),
            ("── Averages (ostatnie) ─────────────────", None),
            ("Ao5",                 self._fmts(self._ao_n(5))),
            ("Ao12",                self._fmts(self._ao_n(12))),
            ("Ao50",                self._fmts(self._ao_n(50))),
            ("Ao100",               self._fmts(self._ao_n(100))),
            ("Ao1000",              self._fmts(self._ao_n(1000))),
            ("── Najlepsze averages ───────────────────", None),
            ("Najlepsze Ao5",       self._fmts(self._best_ao_n(5))),
            ("Najlepsze Ao12",      self._fmts(self._best_ao_n(12))),
            ("Najlepsze Ao50",      self._fmts(self._best_ao_n(50))),
            ("Najlepsze Ao100",     self._fmts(self._best_ao_n(100))),
            ("Najlepsze Ao1000",    self._fmts(self._best_ao_n(1000))),
        ]
        self._stats_data = rows

        for i, (lbl, val) in enumerate(rows):
            if val is None:
                ctk.CTkLabel(self._stats_sf, text=lbl,
                             font=ctk.CTkFont(size=10), text_color="gray50",
                             anchor="w").grid(row=i, column=0, columnspan=2,
                             sticky="ew", padx=8, pady=(10, 2))
            else:
                bg = ("gray82", "gray20") if i % 2 == 0 else ("gray78", "gray17")
                rf = ctk.CTkFrame(self._stats_sf, fg_color=bg, corner_radius=4)
                rf.grid(row=i, column=0, columnspan=2, sticky="ew", padx=4, pady=1)
                rf.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(rf, text=lbl, font=ctk.CTkFont(size=12),
                             anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=4)
                ctk.CTkLabel(rf, text=val,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             anchor="e").grid(row=0, column=1, sticky="e", padx=10, pady=4)

    def _copy_stats(self):
        lines = []
        for lbl, val in self._stats_data:
            lines.append(lbl if val is None else f"{lbl}: {val}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))

    # ── Tab: Wizualizacja ─────────────────────────────────────────

    def _build_viz(self, tab):
        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.pack(fill="x", padx=6, pady=(6, 2))
        ctk.CTkButton(bar, text="Aktualizuj", width=100, height=28,
                      command=self.refresh_viz).pack(side="left")
        self._viz_info = ctk.CTkLabel(bar, text="", text_color="gray55",
                                      font=ctk.CTkFont(size=11))
        self._viz_info.pack(side="left", padx=12)

        self._viz_outer = ctk.CTkFrame(tab, fg_color="transparent")
        self._viz_outer.pack(fill="both", expand=True, padx=6, pady=(2, 6))

        self._viz_canvas = tk.Canvas(self._viz_outer, bg="#16162a",
                                      highlightthickness=0)
        self._viz_canvas.pack(fill="both", expand=True)

        self._viz_na = ctk.CTkLabel(
            self._viz_outer,
            text="Wizualizacja dostępna tylko dla 3×3",
            font=ctk.CTkFont(size=15), text_color="gray50")

        def _on_resize(e):
            if self._viz_resize_id:
                self.after_cancel(self._viz_resize_id)
            self._viz_resize_id = self.after(80, self.refresh_viz)
        self._viz_canvas.bind("<Configure>", _on_resize)

    def refresh_viz(self):
        puzzle   = self._app.puzzle_var.get()
        scramble = self._app.scramble

        state = _make_viz_state(puzzle, scramble)
        if state is None:
            self._viz_canvas.pack_forget()
            self._viz_na.configure(text=f"Brak wizualizacji dla {puzzle}")
            self._viz_na.pack(expand=True)
            self._viz_info.configure(text=f"Puzzle: {puzzle}")
            return

        self._viz_na.pack_forget()
        self._viz_canvas.pack(fill="both", expand=True)
        self._viz_info.configure(text="")

        self._viz_canvas.update_idletasks()
        w = self._viz_canvas.winfo_width()
        h = self._viz_canvas.winfo_height()
        if w < 30 or h < 30:
            if self.winfo_exists():
                self.after(80, self.refresh_viz)
            return

        nc, nr = _viz_net_dims(state)
        cell = min(w // (nc+1), h // (nr+1))
        if cell < 4:
            return
        x0 = (w - nc * cell) // 2
        y0 = (h - nr * cell) // 2

        self._viz_canvas.delete("all")
        state.draw_net(self._viz_canvas, x0, y0, cell)

        short = scramble[:90] + ("…" if len(scramble) > 90 else "")
        self._viz_canvas.create_text(
            w // 2, y0 + nr * cell + max(4, cell // 3),
            text=short, fill="#666677",
            font=("Consolas", max(7, cell // 3)), anchor="n",
        )

    # ── Tab: Metronom ─────────────────────────────────────────────

    def _build_metro(self, tab):
        ctk.CTkLabel(tab, text="Metronom ćwiczeniowy",
                     font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(22, 4))
        ctk.CTkLabel(tab,
                     text="Sygnał dźwiękowy co X sekund — np. \"Zrób solv i zacznij nowy\"",
                     font=ctk.CTkFont(size=11), text_color="gray55").pack(pady=(0, 18))

        row = ctk.CTkFrame(tab, fg_color="transparent")
        row.pack()
        ctk.CTkLabel(row, text="Interwał:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0,10))
        self._metro_var = ctk.IntVar(value=20)
        self._metro_val_lbl = ctk.CTkLabel(row, text="20 s",
                                            font=ctk.CTkFont(size=13, weight="bold"), width=50)
        self._metro_val_lbl.pack(side="right", padx=(10, 0))

        def on_slide(v):
            iv = int(float(v))
            self._metro_var.set(iv)
            self._metro_val_lbl.configure(text=f"{iv} s")
            self._metro_interval = iv

        ctk.CTkSlider(tab, from_=5, to=120, number_of_steps=115,
                      variable=self._metro_var, command=on_slide,
                      width=320).pack(pady=(6, 2))

        hint = ctk.CTkFrame(tab, fg_color="transparent")
        hint.pack()
        ctk.CTkLabel(hint, text="5 s", font=ctk.CTkFont(size=10),
                     text_color="gray55").pack(side="left")
        ctk.CTkLabel(hint, text="120 s", font=ctk.CTkFont(size=10),
                     text_color="gray55").pack(side="right", padx=(280, 0))

        self._metro_cd = ctk.CTkLabel(tab, text="",
                                       font=ctk.CTkFont(size=42, weight="bold"),
                                       text_color="#3dbb77")
        self._metro_cd.pack(pady=(20, 2))

        self._metro_status = ctk.CTkLabel(tab, text="Zatrzymany",
                                           font=ctk.CTkFont(size=12),
                                           text_color="gray55")
        self._metro_status.pack(pady=(0, 16))

        self._metro_btn = ctk.CTkButton(tab, text="▶  Start",
                                         width=150, height=44,
                                         font=ctk.CTkFont(size=15, weight="bold"),
                                         command=self._metro_toggle)
        self._metro_btn.pack()

        if not _HAS_WINSOUND:
            ctk.CTkLabel(tab,
                         text="⚠  winsound niedostępny (tylko Windows)",
                         text_color="gray55", font=ctk.CTkFont(size=10)).pack(pady=(10, 0))

    def _metro_toggle(self):
        if self._metro_running:
            self._metro_stop.set()
            self._metro_running = False
            self._metro_btn.configure(text="▶  Start")
            self._metro_status.configure(text="Zatrzymany")
            self._metro_cd.configure(text="")
        else:
            self._metro_stop.clear()
            self._metro_running  = True
            self._metro_interval = self._metro_var.get()
            self._metro_next     = time.perf_counter() + self._metro_interval
            self._metro_btn.configure(text="⏹  Stop")
            self._metro_status.configure(text="Działa…")
            threading.Thread(target=self._metro_loop, daemon=True).start()
            self._metro_tick()

    def _metro_loop(self):
        while not self._metro_stop.is_set():
            now  = time.perf_counter()
            wait = self._metro_next - now
            if wait <= 0:
                if _HAS_WINSOUND:
                    _winsound.Beep(880, 80)
                self._metro_next += self._metro_interval
            else:
                self._metro_stop.wait(min(wait, 0.05))

    def _metro_tick(self):
        if not self._metro_running:
            return
        rem = max(0.0, self._metro_next - time.perf_counter())
        self._metro_cd.configure(text=f"{rem:.1f}s")
        self.after(100, self._metro_tick)

    # ── public refresh API ────────────────────────────────────────

    def refresh_after_solve(self):
        # Debounced and only for the tab you're looking at: redrawing three
        # matplotlib figures after every solve was a visible hitch.
        if self._refresh_id is not None:
            self.after_cancel(self._refresh_id)
        self._refresh_id = self.after(250, self._refresh_current)

    def _refresh_current(self):
        self._refresh_id = None
        tab = self._tabs.get()
        if "Wykres" in tab:       self.refresh_chart()
        elif "Histogram" in tab:  self.refresh_histogram()
        elif "Statystyki" in tab: self.refresh_stats()
        elif "Wizualizacja" in tab: self.refresh_viz()

    # ── close ─────────────────────────────────────────────────────

    def _on_close(self):
        self._metro_stop.set()
        self._metro_running = False
        self.destroy()

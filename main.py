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

from utils import fmt, display, effective, _bring_to_front, _HAS_WINSOUND, _winsound
from scramble import PUZZLES
from persistence import BASE_DIR, DATA_DIR, DATA_FILE, CFG_FILE, ICON_FILE, Config, Sessions
from hardware_timer import MoyuInput, _load_sounddevice, _moyu_mode
from cube_sim import _make_viz_state, _viz_net_dims
from ui.manual_time_dialog import ManualTimeDialog
from ui.time_detail_dialog import TimeDetailDialog
from ui.stat_detail_dialog import StatDetailDialog
from ui.settings_window import SettingsWindow

# matplotlib is only used inside the Tools window (charts + histogram).  Importing
# it eagerly adds ~500 ms to the cold startup — instead we load it lazily the
# first time a chart is actually built.
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



# Windows: set app ID so taskbar shows custom icon (not generic Python icon)
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "rubiks.timer.app.1"
    )
except Exception:
    pass




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

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self.lift()
        self.focus_set()

    # ── build ─────────────────────────────────────────────────────

    def _build(self):
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=8, pady=8)
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

    def _valid(self):
        return [effective(e) for e in self._times() if effective(e) != float("inf")]

    def _ao_n(self, n, times=None):
        t = times if times is not None else self._times()
        if len(t) < n: return None
        sub = sorted(effective(e) for e in t[-n:])
        trimmed = sub[1:-1]
        if any(v == float("inf") for v in trimmed): return float("inf")
        return sum(trimmed) / len(trimmed)

    def _best_ao_n(self, n):
        times = self._times()
        if len(times) < n: return None
        best = float("inf")
        for i in range(n - 1, len(times)):
            sub = sorted(effective(e) for e in times[i-n+1:i+1])
            trimmed = sub[1:-1]
            if any(v == float("inf") for v in trimmed): continue
            val = sum(trimmed) / len(trimmed)
            if val < best: best = val
        return best if best < float("inf") else None

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
            ax.plot(xs, ys, color="#3dbb77", lw=1.2, alpha=0.75, zorder=2)
            ax.scatter(xs, ys, color="#3dbb77", s=12, zorder=3)

        top_y = max(ys) * 1.08 if ys else 60
        if xs_bad:
            ax.scatter(xs_bad, [top_y] * len(xs_bad),
                       color="#ff5555", s=22, marker="x", zorder=4, label="DNF/DNS")

        # rolling ao5
        # _ao_n only ever looks at the last n elements of what it's given
        # (t[-n:]), so passing the whole times[:i+1] growing prefix on every
        # iteration was an O(n^2) chain of prefix copies for no reason - a
        # fixed n-sized slice gives the exact same result.
        ao5_pts = []
        for i in range(4, len(times)):
            v = self._ao_n(5, times[i-4:i+1])
            if v and v != float("inf"):
                ao5_pts.append((i + 1, v))
        if ao5_pts:
            ax.plot([p[0] for p in ao5_pts], [p[1] for p in ao5_pts],
                    color="#ffaa33", lw=1.6, label="Ao5", zorder=5)

        # rolling ao12
        ao12_pts = []
        for i in range(11, len(times)):
            v = self._ao_n(12, times[i-11:i+1])
            if v and v != float("inf"):
                ao12_pts.append((i + 1, v))
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

        dnf_n = sum(1 for e in times if e.get("penalty") in ("DNF","DNS") or
                    (e.get("penalty") == "DNF"))
        dns_n = sum(1 for e in times if e.get("penalty") == "DNS")
        dnf_n = sum(1 for e in times if effective(e) == float("inf"))

        median_v = std_v = None
        if valid:
            srt = sorted(valid)
            n   = len(srt)
            median_v = srt[n//2] if n % 2 else (srt[n//2-1] + srt[n//2]) / 2
            if n >= 2:
                mean = sum(valid) / n
                std_v = math.sqrt(sum((x - mean)**2 for x in valid) / n)

        rows = [
            ("── Ogólne ──────────────────────────────",  None),
            ("Wszystkich solvów",   str(len(times))),
            ("Valid (bez DNF/DNS)", str(len(valid))),
            ("DNF / DNS",           str(dnf_n)),
            ("── Czasy ───────────────────────────────",  None),
            ("Najlepszy",           self._fmts(min(valid) if valid else None)),
            ("Najgorszy",           self._fmts(max(valid) if valid else None)),
            ("Średnia sesji",       self._fmts(sum(valid)/len(valid) if valid else None)),
            ("Mediana",             self._fmts(median_v)),
            ("Odch. std.",          self._fmts(std_v)),
            ("── Averages (ostatnie) ─────────────────", None),
            ("Ao5",                 self._fmts(self._ao_n(5))),
            ("Ao12",                self._fmts(self._ao_n(12))),
            ("Ao50",                self._fmts(self._ao_n(50))),
            ("Ao100",               self._fmts(self._ao_n(100))),
            ("── Najlepsze averages ───────────────────", None),
            ("Najlepsze Ao5",       self._fmts(self._best_ao_n(5))),
            ("Najlepsze Ao12",      self._fmts(self._best_ao_n(12))),
            ("Najlepsze Ao50",      self._fmts(self._best_ao_n(50))),
            ("Najlepsze Ao100",     self._fmts(self._best_ao_n(100))),
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
        self.refresh_chart()
        self.refresh_histogram()
        self.refresh_stats()

    # ── close ─────────────────────────────────────────────────────

    def _on_close(self):
        self._metro_stop.set()
        self._metro_running = False
        self.destroy()


# ══════════════════════════════════════════════════════════════════
#  Main App
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#  External hardware timer over the audio jack (MoYu / StackMat)
# ══════════════════════════════════════════════════════════════════



class App(ctk.CTk):
    IDLE="idle"; READY="ready"; INSPECTION="inspection"
    RUNNING="running"; STOPPED="stopped"; MANUAL_INPUT="manual_input"

    def __init__(self):
        super().__init__()
        self.title("Wróbel Timer")
        self.geometry("1020x700")
        self.minsize(820, 560)
        if os.path.exists(ICON_FILE):
            self.iconbitmap(ICON_FILE)
            self.after(200, lambda: self.iconbitmap(ICON_FILE))

        self.cfg   = Config()
        self.sm    = Sessions()
        self.cur   = self.sm.last
        self._state = self.IDLE
        self.start_t      = None
        self.insp_t       = None
        self.space_down   = False
        self.scramble     = ""
        self._insp_pen    = None
        self._insp_beeped = set()
        self._row_widgets = []
        self._settings_win = None
        self._tools_win    = None
        self._detail_win   = None
        self._stat_win     = None
        self._notes_win    = None
        self._scramble_hist: list = []
        self._scramble_idx: int  = -1
        self._manual_buf: str   = ""
        self._top_row             = None
        self._streak: int         = 0
        self._focus_mode: bool    = False

        # external audio timer (MoYu / StackMat) — mode from settings
        self._moyu = MoyuInput(self.cfg.g("moyu", "type"))
        self._moyu_last_ms   = None
        self._moyu_stable_t  = 0.0
        self._moyu_phase     = 'idle'   # idle / run / pending / done
        self._moyu_rises     = 0
        self._moyu_run_start = 0.0
        self._moyu_pending_ms = 0
        self._moyu_pending_t  = 0.0
        self._moyu_cand       = -1
        self._moyu_med        = []
        self._moyu_ran        = False
        self._moyu_armed      = True
        self._moyu_lastnz     = 0
        self._moyu_dbg_last   = None
        self._moyu_hist       = []
        self._moyu_zeroed     = False
        self._moyu_prevcur    = 0
        self._moyu_recorded   = False
        self._stk_armed       = False
        self._stk_last_t      = 0
        self._stk_dbg_last    = None
        self._stk_run         = False

        ctk.set_appearance_mode(self.cfg.g("theme"))

        self._build_ui()
        self._load_session(self.cur)
        self._apply_settings()
        if self.cfg.g("show_main_viz"):
            self._toggle_main_viz()
        self._tick()
        # Pre-warm heavy imports on background threads (~200 ms saved on cold
        # start).  If the user opens Charts or the audio timer panel later,
        # everything is already loaded and the UI stays instant.
        threading.Thread(target=_load_sounddevice, daemon=True).start()
        threading.Thread(target=_load_mpl,         daemon=True).start()
        if self.cfg.g("moyu", "enabled"):
            # deferred: start audio after libraries are loaded
            def _late_moyu():
                if MoyuInput.available():
                    self._moyu.start(self.cfg.g("moyu", "device"))
            self.after(300, _late_moyu)
        self.after(100, self._moyu_poll)

        self.bind("<KeyPress-space>",   self._kdown)
        self.bind("<KeyRelease-space>", self._kup)
        self.bind("<m>", lambda _: self._manual_time())
        self.bind("<M>", lambda _: self._manual_time())
        self.bind("<v>", lambda _: self._toggle_main_viz())
        self.bind("<V>", lambda _: self._toggle_main_viz())
        for d in "0123456789":
            self.bind(d, self._manual_key_press)
        self.bind("<BackSpace>", self._manual_backspace)
        self.bind("<Return>",    self._manual_confirm)
        self.bind("<KP_Enter>",  self._manual_confirm)
        self.bind("<Escape>", self._on_escape)
        self.bind("<F11>",    lambda _: self._toggle_fullscreen())
        self.bind("<f>",      lambda _: self._toggle_focus())
        self.bind("<F>",      lambda _: self._toggle_focus())
        self.focus_set()

    # ── build UI ──────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(3, weight=1)

        # ── header ──
        hdr = ctk.CTkFrame(self, corner_radius=0, height=54,
                            fg_color=("gray88","gray14"))
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)
        self._hdr_frame = hdr

        ctk.CTkLabel(hdr, text="  ⏱  Wróbel Timer",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=16, pady=12, sticky="w")

        bar = ctk.CTkFrame(hdr, fg_color="transparent")
        bar.grid(row=0, column=2, padx=12, pady=8, sticky="e")

        ctk.CTkLabel(bar, text="Puzzle:", font=ctk.CTkFont(size=12),
                     text_color="gray60").pack(side="left", padx=(0,4))
        self.puzzle_var = ctk.StringVar()
        ctk.CTkOptionMenu(bar, variable=self.puzzle_var, values=list(PUZZLES),
                          width=114, height=30,
                          command=self._on_puzzle).pack(side="left", padx=(0,16))

        ctk.CTkLabel(bar, text="Sesja:", font=ctk.CTkFont(size=12),
                     text_color="gray60").pack(side="left", padx=(0,4))
        self.session_var  = ctk.StringVar()
        self.session_menu = ctk.CTkOptionMenu(bar, variable=self.session_var,
                                              values=self.sm.names, width=176, height=30,
                                              command=self._on_session)
        self.session_menu.pack(side="left", padx=(0,2))
        self.session_menu.bind("<Double-Button-1>",
                               lambda e: self._rename_current_session())
        ctk.CTkButton(bar, text="✏", width=28, height=30,
                      fg_color="gray25", hover_color="gray35",
                      font=ctk.CTkFont(size=13),
                      command=self._rename_current_session).pack(side="left", padx=(0,2))
        ctk.CTkButton(bar, text="📝", width=28, height=30,
                      fg_color="gray25", hover_color="gray35",
                      font=ctk.CTkFont(size=13),
                      command=self._open_notes).pack(side="left", padx=(0,8))
        ctk.CTkButton(bar, text="+ Nowa", width=76, height=30,
                      command=self._new_session).pack(side="left", padx=(0,8))
        ctk.CTkButton(bar, text="📈 Narzędzia", width=110, height=30,
                      command=self._open_tools).pack(side="left", padx=(0,6))
        ctk.CTkButton(bar, text="⚙", width=36, height=30,
                      command=self._open_settings).pack(side="left", padx=(0,6))
        self._fs_btn = ctk.CTkButton(bar, text="⛶", width=36, height=30,
                      fg_color="gray25", hover_color="gray35",
                      font=ctk.CTkFont(size=16),
                      command=self._toggle_fullscreen)
        self._fs_btn.pack(side="left", padx=(0,6))
        self._focus_btn = ctk.CTkButton(bar, text="◉", width=36, height=30,
                      fg_color="gray25", hover_color="gray35",
                      font=ctk.CTkFont(size=16),
                      command=self._toggle_focus)
        self._focus_btn.pack(side="left")

        # ── scramble card ──
        sc_card = ctk.CTkFrame(self, corner_radius=12,
                                fg_color=("gray84","gray16"))
        sc_card.grid(row=1, column=0, columnspan=2, padx=16, pady=(10,4), sticky="ew")
        sc_card.grid_columnconfigure(0, weight=1)

        sc_row = ctk.CTkFrame(sc_card, fg_color="transparent")
        sc_row.grid(row=0, column=0, sticky="ew")
        sc_row.grid_columnconfigure(1, weight=1)

        self._btn_prev_scr = ctk.CTkButton(
            sc_row, text="◀", width=34, height=28,
            fg_color="gray25", hover_color="gray35",
            font=ctk.CTkFont(size=13),
            command=self._prev_scramble)
        self._btn_prev_scr.grid(row=0, column=0, padx=(10,4), pady=8)

        self.scramble_var = ctk.StringVar()
        self.scramble_lbl = ctk.CTkLabel(sc_row, textvariable=self.scramble_var,
                                          font=ctk.CTkFont(size=15, weight="bold"),
                                          wraplength=780, justify="center")
        self.scramble_lbl.grid(row=0, column=1, padx=4, pady=10)

        self._btn_next_scr = ctk.CTkButton(
            sc_row, text="▶", width=34, height=28,
            fg_color="gray25", hover_color="gray35",
            font=ctk.CTkFont(size=13),
            command=self._next_scramble)
        self._btn_next_scr.grid(row=0, column=2, padx=(4,6), pady=8)

        self._main_viz_on  = False
        self._viz_main_btn = ctk.CTkButton(
            sc_row, text="🎲", width=34, height=28,
            fg_color="gray25", hover_color="gray35",
            font=ctk.CTkFont(size=14),
            command=self._toggle_main_viz)
        self._viz_main_btn.grid(row=0, column=3, padx=(0,10), pady=8)

        # ── hint row ──
        hrow = ctk.CTkFrame(self, fg_color="transparent")
        hrow.grid(row=2, column=0, columnspan=2, padx=16, pady=(0,2), sticky="ew")

        self.hint_var = ctk.StringVar(value="Przytrzymaj SPACJĘ żeby przygotować start")
        ctk.CTkLabel(hrow, textvariable=self.hint_var,
                     font=ctk.CTkFont(size=12), text_color="gray55").pack(side="left")

        self._insp_on = ctk.BooleanVar(value=self.cfg.g("timer","inspection_enabled"))
        ctk.CTkCheckBox(hrow, text="Inspekcja", variable=self._insp_on,
                        font=ctk.CTkFont(size=12),
                        command=lambda: self.cfg.s("timer","inspection_enabled",
                                                   self._insp_on.get())).pack(side="right")

        # ── timer row (container split: left viz + timer) ──
        self.timer_var = ctk.StringVar(value="0.000")

        self._timer_container = ctk.CTkFrame(self, fg_color="transparent")
        self._timer_container.grid(row=3, column=0, sticky="nsew")
        self._timer_container.grid_columnconfigure(0, weight=0)
        self._timer_container.grid_columnconfigure(1, weight=1)
        self._timer_container.grid_rowconfigure(0, weight=1)

        self._left_viz_frame = ctk.CTkFrame(
            self._timer_container, fg_color=("#cccccc", "#16162a"),
            corner_radius=8, width=175)
        self._left_viz_frame.grid_propagate(False)
        self._left_viz_canvas = tk.Canvas(
            self._left_viz_frame, bg="#16162a",
            highlightthickness=0, width=175)
        self._left_viz_canvas.pack(fill="both", expand=True, padx=4, pady=6)
        self._left_viz_canvas.bind("<Configure>", lambda e: self._refresh_main_viz())

        self.timer_lbl = ctk.CTkLabel(
            self._timer_container, textvariable=self.timer_var,
            font=ctk.CTkFont(size=88, weight="bold"),
            text_color="white")
        self.timer_lbl.grid(row=0, column=1, padx=6, sticky="nsew")

        # ── target feedback label ──
        self._target_lbl = ctk.CTkLabel(self, text="",
                                         font=ctk.CTkFont(size=16, weight="bold"))
        self._target_lbl.grid(row=3, column=0, padx=24, sticky="s", pady=(0,4))

        # ── penalty buttons ──
        self.pen_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pen_frame.grid(row=4, column=0, padx=24, pady=(0,8))
        self._pen_btns = {}
        for p in ["+2","DNF","DNS"]:
            b = ctk.CTkButton(self.pen_frame, text=p, width=78, height=32,
                              font=ctk.CTkFont(size=13, weight="bold"),
                              fg_color="gray22", hover_color="gray30",
                              corner_radius=8,
                              command=lambda x=p: self._pen_click(x))
            b.pack(side="left", padx=5)
            self._pen_btns[p] = b
        self.pen_frame.grid_remove()

        # ── right panel ──
        rp = ctk.CTkFrame(self, width=228, corner_radius=12)
        self._rp_frame = rp
        rp.grid(row=3, column=1, rowspan=2, padx=(0,16), pady=(8,4), sticky="nsew")
        rp.grid_rowconfigure(1, weight=1)
        rp.grid_columnconfigure(0, weight=1)
        rp.grid_propagate(False)

        rp_hdr = ctk.CTkFrame(rp, fg_color="transparent")
        rp_hdr.grid(row=0, column=0, sticky="ew", padx=8, pady=(8,2))
        rp_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(rp_hdr, text="Czasy",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w")
        rp_btns = ctk.CTkFrame(rp_hdr, fg_color="transparent")
        rp_btns.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(rp_btns, text="💾", width=32, height=26,
                      font=ctk.CTkFont(size=13),
                      fg_color="gray25", hover_color="gray35",
                      command=self._export_session).pack(side="left", padx=(0,4))
        ctk.CTkButton(rp_btns, text="⌨  Wpisz", width=86, height=26,
                      font=ctk.CTkFont(size=11),
                      fg_color="gray25", hover_color="gray35",
                      command=self._manual_time).pack(side="left")

        self.list_frame = ctk.CTkScrollableFrame(rp, fg_color="transparent",
                                                  corner_radius=0)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0,6))

        # ── stats bar ──
        self.stats_card = ctk.CTkFrame(self, corner_radius=12, height=72)
        self.stats_card.grid(row=5, column=0, columnspan=2,
                             padx=16, pady=(4,14), sticky="ew")
        self.stat_lbl = {}
        self._rebuild_stats()

    # ── stats bar ─────────────────────────────────────────────────

    def _rebuild_stats(self):
        for w in self.stats_card.winfo_children(): w.destroy()
        self.stat_lbl.clear()

        defs = []
        if self.cfg.g("stats","show_best"):  defs.append(("Najlepszy","best"))
        if self.cfg.g("stats","show_ao5"):   defs.append(("Ao5","ao5"))
        if self.cfg.g("stats","show_ao12"):  defs.append(("Ao12","ao12"))
        if self.cfg.g("stats","show_ao100"): defs.append(("Ao100","ao100"))
        if self.cfg.g("stats","show_mean"):  defs.append(("Śr. sesji","mean"))
        for n in self.cfg.g("stats","custom_averages"):
            defs.append((f"Ao{n}", f"_cao_{n}"))
        defs.append(("Solvów","count"))

        clickable = {"best","ao5","ao12","ao100","mean"} | {f"_cao_{n}" for n in self.cfg.g("stats","custom_averages")}

        for i in range(len(defs)):
            self.stats_card.grid_columnconfigure(i, weight=1)
        for i,(title,key) in enumerate(defs):
            is_click = key in clickable

            ctk.CTkLabel(self.stats_card, text=title, font=ctk.CTkFont(size=11),
                         text_color="gray55").grid(row=0, column=i, padx=6, pady=(8,0))

            if is_click:
                l = ctk.CTkButton(
                    self.stats_card, text="—",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    fg_color="transparent",
                    hover_color=("gray78","gray22"),
                    text_color=("gray10","gray90"),
                    border_width=0, corner_radius=6,
                    cursor="hand2", height=32,
                    command=lambda k=key: self._show_stat_detail(k))
                l.grid(row=1, column=i, padx=4, pady=(0,6), sticky="ew")
            else:
                l = ctk.CTkLabel(self.stats_card, text="—",
                                 font=ctk.CTkFont(size=18, weight="bold"))
                l.grid(row=1, column=i, padx=6, pady=(0,8))
            self.stat_lbl[key] = l

    # ── apply settings ────────────────────────────────────────────

    def _apply_settings_debounced(self):
        """Wersja z 150ms opóźnieniem — używana przez SettingsWindow żeby nie migało."""
        if getattr(self, "_apply_id", None):
            self.after_cancel(self._apply_id)
        self._apply_id = self.after(150, self._apply_settings)

    def _apply_settings(self):
        # UI zoom — tylko gdy wartość się zmieniła (kosztowna operacja)
        zoom = self.cfg.g("ui_zoom")
        if getattr(self, "_last_zoom", None) != zoom:
            try:
                ctk.set_widget_scaling(zoom)
            except Exception:
                pass
            self._last_zoom = zoom

        sz     = self.cfg.g("font", "timer_size")
        family = self.cfg.g("font", "timer_family")
        if family and family != "Default":
            self.timer_lbl.configure(font=ctk.CTkFont(family=family, size=sz, weight="bold"))
        else:
            self.timer_lbl.configure(font=ctk.CTkFont(size=sz, weight="bold"))

        sc_sz     = self.cfg.g("font", "scramble_size")
        sc_col    = self.cfg.g("colors", "scramble")
        sc_family = self.cfg.g("font", "scramble_family")
        align     = self.cfg.g("scramble_align")
        sc_anchor = {"left": "w", "center": "center", "right": "e"}.get(align, "center")
        sc_kw = dict(font=ctk.CTkFont(
                         family=sc_family if sc_family and sc_family != "Default" else "Segoe UI",
                         size=sc_sz, weight="bold"),
                     text_color=sc_col,
                     justify=align, anchor=sc_anchor)
        self.scramble_lbl.configure(**sc_kw)

        self._insp_on.set(self.cfg.g("timer","inspection_enabled"))
        self._set_timer_color(self._state)

        # _rebuild_stats tylko gdy konfiguracja statystyk się zmieniła
        stats_key = str(self.cfg.g("stats"))
        if getattr(self, "_last_stats_cfg", None) != stats_key:
            self._rebuild_stats()
            self._last_stats_cfg = stats_key
        self._update_stats()

        bg_win = self.cfg.g("colors", "bg_window")
        if bg_win:
            self.configure(fg_color=bg_win)
        bg_hdr = self.cfg.g("colors", "bg_header")
        if bg_hdr and hasattr(self, "_hdr_frame"):
            self._hdr_frame.configure(fg_color=bg_hdr)

    def _set_timer_color(self, state):
        pen_active = False
        if state == self.STOPPED:
            times = self.sm.get(self.cur)["times"]
            if times and times[-1].get("penalty") in ("DNF","DNS"):
                pen_active = True
        if pen_active:
            self.timer_lbl.configure(text_color=self.cfg.g("colors","timer_penalty"))
        elif state == self.READY:
            self.timer_lbl.configure(text_color=self.cfg.g("colors","timer_ready"))
        elif state == self.INSPECTION:
            self.timer_lbl.configure(text_color=self.cfg.g("colors","timer_inspection"))
        elif state == self.RUNNING:
            self.timer_lbl.configure(text_color=self.cfg.g("colors","timer_running"))
        elif state == self.MANUAL_INPUT:
            self.timer_lbl.configure(text_color="#44AAFF")
        else:
            self.timer_lbl.configure(text_color=self.cfg.g("colors","timer_idle"))

    # ── session ───────────────────────────────────────────────────

    def _load_session(self, name):
        self.cur = name
        sess = self.sm.get(name)
        self.session_var.set(name)
        self.session_menu.configure(values=self.sm.names)
        self.puzzle_var.set(sess["puzzle"])
        self._scramble_hist.clear()
        self._scramble_idx = -1

        # bump generation so any background loader from a previous session dies
        self._load_gen = getattr(self, "_load_gen", 0) + 1
        for w, _, _ in self._row_widgets:
            if w: w.destroy()
        self._row_widgets.clear(); self._top_row = None

        # Only the newest ~40 rows are built synchronously; the rest fills in
        # from a background task so a big session (hundreds of solves) opens
        # instantly instead of freezing for seconds.
        times = sess["times"]; N = len(times)
        SYNC = 40
        for e in times[:min(N, SYNC)]:
            self._add_row(e)
        if N > SYNC:
            gen = self._load_gen
            rest = list(times[SYNC:])
            def _bg():
                if gen != self._load_gen or not rest: return
                for _ in range(min(30, len(rest))):
                    self._add_row(rest.pop(0))
                if rest: self.after(10, _bg)
            self.after(30, _bg)

        self._update_stats()
        self._new_scramble()

    def _on_session(self, name):
        self.sm.switch(name); self._load_session(name)

    def _on_puzzle(self, puzzle):
        self.sm.set_puzzle(self.cur, puzzle); self._new_scramble()

    def _new_session(self):
        name = sd.askstring("Nowa sesja","Nazwa:", parent=self)
        if not name or not name.strip() or name.strip() in self.sm.names: return
        self.sm.create(name.strip(), self.puzzle_var.get())
        self.session_menu.configure(values=self.sm.names)
        self._load_session(name.strip())

    def _new_scramble(self):
        s = PUZZLES[self.puzzle_var.get()]()
        # truncate forward history when generating fresh (after a solve or puzzle change)
        if self._scramble_idx < len(self._scramble_hist) - 1:
            self._scramble_hist = self._scramble_hist[:self._scramble_idx + 1]
        self._scramble_hist.append(s)
        self._scramble_idx = len(self._scramble_hist) - 1
        self._show_scramble(s)

    def _show_scramble(self, s):
        self.scramble = s
        self.scramble_var.set(s)
        if self._tools_win and self._tools_win.winfo_exists():
            self._tools_win.refresh_viz()
        self._refresh_main_viz()
        self._update_nav_btns()

    def _update_nav_btns(self):
        if not hasattr(self, "_btn_prev_scr"): return
        can_prev = self._scramble_idx > 0
        can_next = True  # can always go next (generates new if at end)
        self._btn_prev_scr.configure(state="normal" if can_prev else "disabled",
                                     fg_color="gray25" if can_prev else "gray18")

    def _prev_scramble(self):
        if self._scramble_idx <= 0: return
        self._scramble_idx -= 1
        self._show_scramble(self._scramble_hist[self._scramble_idx])

    def _next_scramble(self):
        if self._scramble_idx < len(self._scramble_hist) - 1:
            self._scramble_idx += 1
            self._show_scramble(self._scramble_hist[self._scramble_idx])
        else:
            self._new_scramble()

    # ── tick ──────────────────────────────────────────────────────

    def _tick(self):
        if self._state == self.INSPECTION:
            elapsed = time.perf_counter() - self.insp_t
            rem = self.cfg.g("timer","inspection_duration") - elapsed
            if rem > 0:
                self.timer_var.set(str(int(rem)+1))
                self._set_timer_color(self.INSPECTION)
            elif rem > -2:
                self.timer_var.set("+2")
                self.timer_lbl.configure(text_color=self.cfg.g("colors","timer_penalty"))
            else:
                self._state = self.STOPPED
                self._record(0.0, "DNF")
            if _HAS_WINSOUND:
                if elapsed >= 8 and 8 not in self._insp_beeped:
                    self._insp_beeped.add(8)
                    threading.Thread(target=lambda: _winsound.Beep(880, 120), daemon=True).start()
                if elapsed >= 12 and 12 not in self._insp_beeped:
                    self._insp_beeped.add(12)
                    threading.Thread(target=lambda: _winsound.Beep(660, 200), daemon=True).start()

        elif self._state == self.RUNNING:
            el = time.perf_counter() - self.start_t
            if self.cfg.g("timer","hide_during_solve"):
                self.timer_var.set("••••")
            else:
                self.timer_var.set(fmt(el, self.cfg.g("timer","decimals")))

        self.after(self.cfg.g("timer", "refresh_ms"), self._tick)

    # ── keyboard ──────────────────────────────────────────────────

    def _kdown(self, _e):
        if self.space_down: return
        self.space_down = True

        if self._state == self.MANUAL_INPUT:
            self._manual_cancel()

        if self._state in (self.IDLE, self.STOPPED):
            self._state = self.READY
            self._set_timer_color(self.READY)
            self.hint_var.set("Puść SPACJĘ żeby wystartować")
            self.pen_frame.grid_remove()

        elif self._state == self.INSPECTION:
            self._start()

        elif self._state == self.RUNNING:
            el = time.perf_counter() - self.start_t
            self._state = self.STOPPED
            self._record(el, self._insp_pen)
            self._insp_pen = None

    def _kup(self, _e):
        self.space_down = False
        if self._state != self.READY: return

        delay = self.cfg.g("timer","start_delay_ms")
        if self._insp_on.get():
            self._state = self.INSPECTION
            self.insp_t = time.perf_counter()
            self._insp_beeped.clear()
            dur = self.cfg.g("timer","inspection_duration")
            self.timer_var.set(str(dur))
            self._set_timer_color(self.INSPECTION)
            self.hint_var.set("Naciśnij SPACJĘ żeby pominąć inspekcję")
        else:
            self.after(delay, self._start)

    def _start(self):
        if self.insp_t and (time.perf_counter()-self.insp_t) > self.cfg.g("timer","inspection_duration"):
            self._insp_pen = "+2"
        self.insp_t = None
        self._state  = self.RUNNING
        self.start_t = time.perf_counter()
        self._set_timer_color(self.RUNNING)
        self.hint_var.set("Naciśnij SPACJĘ żeby zatrzymać")

    # ── recording ─────────────────────────────────────────────────

    def _record(self, t, penalty):
        dec   = self.cfg.g("timer","decimals")
        prev_times = self.sm.get(self.cur)["times"]
        prev_best  = min((effective(e) for e in prev_times
                          if effective(e) != float("inf")), default=float("inf"))
        entry = {"time":t, "penalty":penalty, "scramble":self.scramble,
                 "puzzle": self.puzzle_var.get(),
                 "date":datetime.now().isoformat()}
        self.sm.add(self.cur, entry)
        self.timer_var.set(display(entry, dec))
        new_eff = effective(entry)
        is_pb = new_eff != float("inf") and new_eff < prev_best

        if is_pb:
            self.timer_lbl.configure(text_color="#FFD700")
            self.after(1800, lambda: self._set_timer_color(self.STOPPED))
            if self.cfg.g("target","pb_sound") and _HAS_WINSOUND:
                threading.Thread(target=self._play_pb_sound, daemon=True).start()
        else:
            self._set_timer_color(self.STOPPED)

        # ── target / streak ──
        tgt_en  = self.cfg.g("target","enabled")
        tgt_val = self.cfg.g("target","time")
        if tgt_en and new_eff != float("inf"):
            under = new_eff <= tgt_val
            if under:
                self._streak += 1
                diff = tgt_val - new_eff
                self._target_lbl.configure(
                    text=f"✓ -{diff:.2f}s  streak {self._streak}",
                    text_color="#44DD77")
            else:
                self._streak = 0
                diff = new_eff - tgt_val
                self._target_lbl.configure(
                    text=f"✗ +{diff:.2f}s  sub-{tgt_val:.1f}",
                    text_color="#FF5555")
        else:
            self._target_lbl.configure(text="")

        self.hint_var.set("Przytrzymaj SPACJĘ żeby przygotować start")
        self._add_row(entry)
        self._refresh_pen_buttons(penalty)
        self.pen_frame.grid()
        self._update_stats()
        self._new_scramble()
        if self._tools_win and self._tools_win.winfo_exists():
            self._tools_win.refresh_after_solve()

    @staticmethod
    def _play_pb_sound():
        for freq, dur in [(880,80),(1100,80),(1320,120)]:
            _winsound.Beep(freq, dur)

    # ── penalties ─────────────────────────────────────────────────

    def _refresh_pen_buttons(self, active):
        for p, b in self._pen_btns.items():
            if p == active:
                b.configure(fg_color=("#1a5fa0","#1f6aa5"), hover_color=("#155090","#1a5a90"))
            else:
                b.configure(fg_color="gray22", hover_color="gray30")

    def _pen_click(self, pen):
        times = self.sm.get(self.cur)["times"]
        if not times: return
        idx   = len(times)-1
        entry = dict(times[idx])
        entry["penalty"] = None if entry["penalty"]==pen else pen
        self.sm.update(self.cur, idx, entry)
        dec = self.cfg.g("timer","decimals")
        self.timer_var.set(display(entry, dec))
        self._set_timer_color(self.STOPPED)
        self._refresh_pen_buttons(entry["penalty"])
        if self._row_widgets:
            _, lbl, _ = self._row_widgets[-1]
            lbl.configure(text=display(entry, dec))
        self._update_stats()

    # ── times list ────────────────────────────────────────────────

    def _row_index(self, row):
        # Rows can be deleted individually now (see _del_time), so a click
        # handler can't capture a fixed index at creation time - it would go
        # stale for every row after the deleted one. Look it up live instead.
        for i, (r, _, _) in enumerate(self._row_widgets):
            if r is row:
                return i
        return None

    def _add_row(self, entry):
        n   = len(self._row_widgets)+1
        dec = self.cfg.g("timer","decimals")
        bg  = ("gray80","gray20") if n % 2 == 0 else ("gray84","gray17")

        row = ctk.CTkFrame(self.list_frame, fg_color=bg, corner_radius=6, cursor="hand2")
        if self._top_row is not None:
            row.pack(fill="x", padx=4, pady=2, before=self._top_row)
        else:
            row.pack(fill="x", padx=4, pady=2)
        self._top_row = row

        num = ctk.CTkLabel(row, text=f" {n}.", width=28,
                           font=ctk.CTkFont(size=11), text_color="gray55")
        num.pack(side="left")
        tlb = ctk.CTkLabel(row, text=display(entry, dec),
                           font=ctk.CTkFont(size=13, weight="bold"))
        tlb.pack(side="left", padx=(0,6), pady=4)

        for w in (row, num, tlb):
            w.bind("<Button-1>", lambda e, r=row: self._show_detail(self._row_index(r)))
            w.bind("<Button-3>", lambda e, r=row: self._ctx(e, self._row_index(r)))
            w.bind("<Enter>",    lambda e, r=row: r.configure(fg_color=("gray75","gray25")))
            w.bind("<Leave>",    lambda e, r=row, b=bg: r.configure(fg_color=b))

        self._row_widgets.append((row, tlb, num))

    def _ctx(self, event, idx):
        times = self.sm.get(self.cur)["times"]
        if idx >= len(times): return
        entry = times[idx]
        m = tk.Menu(self, tearoff=0)
        for pen in ["+2","DNF","DNS"]:
            chk = "✓  " if entry.get("penalty")==pen else "      "
            m.add_command(label=f"{chk}{pen}",
                          command=lambda p=pen, i=idx: self._set_pen(i,p))
        m.add_separator()
        m.add_command(label="Usuń", command=lambda i=idx: self._del_time(i))
        m.tk_popup(event.x_root, event.y_root)

    def _set_pen(self, idx, pen):
        times = self.sm.get(self.cur)["times"]
        entry = dict(times[idx])
        entry["penalty"] = None if entry["penalty"]==pen else pen
        self.sm.update(self.cur, idx, entry)
        dec = self.cfg.g("timer","decimals")
        _, lbl, _ = self._row_widgets[idx]
        lbl.configure(text=display(entry, dec))
        if self._state==self.STOPPED and idx==len(times)-1:
            self.timer_var.set(display(entry, dec))
            self._set_timer_color(self.STOPPED)
            self._refresh_pen_buttons(entry["penalty"])
        self._update_stats()

    def _show_detail(self, idx):
        if self._detail_win and self._detail_win.winfo_exists():
            self._detail_win.destroy()
        self._detail_win = TimeDetailDialog(self, idx)

    def _show_stat_detail(self, key):
        self._stat_win = StatDetailDialog(self, key)

    def _del_time(self, idx):
        if self._detail_win and self._detail_win.winfo_exists():
            self._detail_win.destroy()
        self._detail_win = None
        if hasattr(self, "_stat_win") and self._stat_win and self._stat_win.winfo_exists():
            self._stat_win.destroy()
        self._stat_win = None
        self.sm.delete(self.cur, idx)
        # Remove just the one row instead of destroying and rebuilding every
        # widget in the list (main.py used to do this on every delete, which
        # freezes the UI for a couple seconds on a large session).
        row, _, _ = self._row_widgets.pop(idx)
        row.destroy()
        self._top_row = self._row_widgets[-1][0] if self._row_widgets else None
        for i in range(idx, len(self._row_widgets)):
            _, _, num_lbl = self._row_widgets[i]
            num_lbl.configure(text=f" {i+1}.")
        self._update_stats()
        if self._tools_win and self._tools_win.winfo_exists():
            self._tools_win.refresh_after_solve()

    # ── stats ─────────────────────────────────────────────────────

    def _ao(self, n):
        times = self.sm.get(self.cur)["times"]
        if len(times) < n: return None
        sub     = sorted(effective(e) for e in times[-n:])
        trimmed = sub[1:-1] if n > 2 else sub
        if not trimmed: return None
        if any(t == float("inf") for t in trimmed): return float("inf")
        return sum(trimmed) / len(trimmed)

    def _mean(self):
        times = self.sm.get(self.cur)["times"]
        vals  = [effective(e) for e in times if effective(e)!=float("inf")]
        return sum(vals)/len(vals) if vals else None

    def _update_stats(self):
        times = self.sm.get(self.cur)["times"]
        dec   = self.cfg.g("timer","decimals")
        valid = [effective(e) for e in times if effective(e)!=float("inf")]

        def _s(key, val):
            if key not in self.stat_lbl: return
            if val is None:              self.stat_lbl[key].configure(text="—")
            elif val==float("inf"):      self.stat_lbl[key].configure(text="DNF")
            else:                        self.stat_lbl[key].configure(text=fmt(val,dec))

        if "count" in self.stat_lbl: self.stat_lbl["count"].configure(text=str(len(times)))
        if "best"  in self.stat_lbl: _s("best",  min(valid) if valid else None)
        if "ao5"   in self.stat_lbl: _s("ao5",   self._ao(5))
        if "ao12"  in self.stat_lbl: _s("ao12",  self._ao(12))
        if "ao100" in self.stat_lbl: _s("ao100", self._ao(100))
        if "mean"  in self.stat_lbl: _s("mean",  self._mean())
        for n in self.cfg.g("stats", "custom_averages"):
            _s(f"_cao_{n}", self._ao(n))

    # ── manual time entry ─────────────────────────────────────────

    def _manual_time(self):
        if self._state in (self.RUNNING, self.MANUAL_INPUT):
            return
        self._state = self.MANUAL_INPUT
        self._manual_buf = ""
        self.timer_var.set("0.00")
        self._set_timer_color(self.MANUAL_INPUT)
        self.hint_var.set("Wpisz czas (np. 1233 = 12.33s)  •  ← cofnij  •  Enter = OK  •  Esc = anuluj")
        self.pen_frame.grid_remove()

    @staticmethod
    def _parse_manual_buf(buf):
        if not buf:
            return 0.0
        cs  = int(buf[-2:]) if len(buf) >= 2 else int(buf)
        sec = int(buf[-4:-2]) if len(buf) >= 4 else (int(buf[:-2]) if len(buf) > 2 else 0)
        mn  = int(buf[:-4]) if len(buf) > 4 else 0
        return mn * 60 + sec + cs / 100

    def _manual_key_press(self, event):
        if self._state != self.MANUAL_INPUT:
            return
        if event.char.isdigit() and len(self._manual_buf) < 7:
            self._manual_buf += event.char
            t = self._parse_manual_buf(self._manual_buf)
            self.timer_var.set(fmt(t, 2))

    def _manual_backspace(self, event=None):
        if self._state != self.MANUAL_INPUT:
            return
        if self._manual_buf:
            self._manual_buf = self._manual_buf[:-1]
            t = self._parse_manual_buf(self._manual_buf)
            self.timer_var.set(fmt(t, 2))

    def _manual_confirm(self, event=None):
        if self._state != self.MANUAL_INPUT:
            return
        if not self._manual_buf:
            self._manual_cancel()
            return
        t   = self._parse_manual_buf(self._manual_buf)
        dec = self.cfg.g("timer", "decimals")
        entry = {
            "time":    t,
            "penalty": None,
            "scramble": self.scramble,
            "date":    datetime.now().isoformat(),
            "manual":  True,
        }
        self.sm.add(self.cur, entry)
        self._add_row(entry)
        self._update_stats()
        self._new_scramble()
        if self._tools_win and self._tools_win.winfo_exists():
            self._tools_win.refresh_after_solve()

        # zostań w trybie wpisywania — wyczyść bufor i czekaj na kolejny czas
        self._manual_buf = ""
        self.timer_var.set("0.00")
        self._set_timer_color(self.MANUAL_INPUT)

    def _manual_cancel(self, event=None):
        if self._state != self.MANUAL_INPUT:
            return
        self._state = self.IDLE
        self._manual_buf = ""
        dec = self.cfg.g("timer", "decimals")
        self.timer_var.set(f"0.{'0'*dec}")
        self._set_timer_color(self.IDLE)
        self.hint_var.set("Przytrzymaj SPACJĘ żeby przygotować start")

    # ── external timer (MoYu / StackMat) ──────────────────────────

    def _moyu_set_enabled(self, on, device="", mode=None):
        self.cfg.s("moyu", "enabled", bool(on))
        if device:
            self.cfg.s("moyu", "device", device)
        if mode:
            self.cfg.s("moyu", "type", mode)
        # rebuild the input if the mode changed
        cur_mode = self.cfg.g("moyu", "type")
        if getattr(self._moyu, "mode", None) != cur_mode:
            try: self._moyu.stop()
            except Exception: pass
            self._moyu = MoyuInput(cur_mode)
        if on:
            self._moyu.start(self.cfg.g("moyu", "device"))
        else:
            self._moyu.stop()

    def _moyu_log(self, line):
        # diagnostic logging disabled — kept as a no-op so any remaining
        # call sites don't need touching
        pass

    def _moyu_poll(self):
        # MoYu decode has NO checksum → readings flicker between the real value
        # and single-bit errors.  So:
        #   • the shown/used value is the MODE of recent readings — the correct
        #     value dominates the scattered errors;
        #   • a solve is committed on the RESET (the value held just before the
        #     timer drops to 0 — the only reliable signal), with a 6 s fallback
        #     if it's left stopped;
        #   • it only counts as a solve once the timer has actually been at 0
        #     (so an idle/old value is never recorded).
        if not (self._moyu and self._moyu.running):
            # Hardware timer feature is off (or not connected): check back
            # occasionally instead of scheduling a permanent 20-50ms tick
            # forever that competes with the Tk event loop for no reason.
            self.after(500, self._moyu_poll)
            return
        try:
            m = self._moyu
            if m and m.running:
                # ── StackMat mode: signal has a checksum + explicit state, so
                # detection is trivial: on transition (anything → 'S') with a
                # non-zero time, record once.  Re-arm when the state changes.
                if getattr(m, "mode", "m") == 's':
                    st = m.latest() or {}
                    on   = bool(st.get("on"))
                    head = st.get("signalHeader", 'I')
                    t    = int(st.get("time_milli", 0))
                    sig  = (on, head, t)
                    if sig != self._stk_dbg_last:
                        self._stk_dbg_last = sig
                        self._moyu_log("STK on=%s head=%r t=%d armed=%s last=%d state=%s"
                                       % (on, head, t, self._stk_armed,
                                          self._stk_last_t, self._state))
                    if on:
                        disp = self._state in (self.IDLE, self.STOPPED)
                        # live mirror + colour on the main timer display (safe
                        # for StackMat because the decode is CRC-verified)
                        if disp:
                            self.timer_var.set(fmt(t / 1000.0,
                                                   self.cfg.g("timer", "decimals")))
                            if head == ' ':
                                self._set_timer_color(self.RUNNING)
                            elif t == 0:
                                self._set_timer_color(self.IDLE)
                        # STOP-detection tuned to what this Gen5 actually sends:
                        #   • head==' ' + rising t = counting
                        #   • t<200        = reset / idle
                        #   • otherwise (head!=' ' + t>=200) after we saw a run
                        #     = the timer just stopped — record once
                        if head == ' ':
                            self._stk_run = True
                        elif t < 200:
                            self._stk_run = False
                            self._stk_last_t = 0     # allow same time next solve
                        elif disp and self._stk_run and t >= 200 and t != self._stk_last_t:
                            self._moyu_log(">>> STK RECORD %.3f" % (t / 1000.0))
                            self._stk_last_t = t
                            self._stk_run = False
                            self._record(t / 1000.0, None)
                    self.after(20, self._moyu_poll); return
                rawnow = int(m.latest().get("time_milli", 0))
                if rawnow != self._moyu_dbg_last:           # DEBUG
                    self._moyu_dbg_last = rawnow
                    self._moyu_log("%.3f\traw=%d\tran=%s\tarmed=%s\tzero=%s" % (
                        time.perf_counter(), rawnow, self._moyu_ran,
                        self._moyu_armed, self._moyu_zeroed))
                now  = time.perf_counter()
                self._moyu_hist.append((rawnow, now))
                while self._moyu_hist and now - self._moyu_hist[0][1] > 6.5:
                    self._moyu_hist.pop(0)
                cur  = _moyu_mode([r for r, t in self._moyu_hist if now - t < 0.6])
                ok   = self._state in (self.IDLE, self.STOPPED)
                prev = self._moyu_prevcur

                def _final():
                    return _moyu_mode([r for r, t in self._moyu_hist
                                       if now - t < 3.0 and r >= 300])

                # MoYu counts up, so the final time MUST be >= the peak seen in
                # the last few seconds.  If a candidate is a lot smaller (e.g.
                # 1.896 instead of 9.847), the decoder lost data mid-count —
                # skip and wait for it to recover.
                def _commit_ok(f):
                    mx = max((r for r, t in self._moyu_hist if now - t < 4.0), default=0)
                    return f >= 200 and f >= int(mx * 0.85)

                if cur < 300:                                # timer at / near 0
                    if ok and self._moyu_ran and not self._moyu_recorded:
                        f = _final()
                        if _commit_ok(f):
                            self._moyu_log(">>> RECORD %.3f" % (f / 1000.0))
                            self._record(f / 1000.0, None)
                        else:
                            self._moyu_log(">>> SKIP(reset) f=%d" % f)
                    # fresh state for the next solve
                    self._moyu_ran = False; self._moyu_recorded = False
                    self._moyu_zeroed = True; self._moyu_stable_t = now
                else:
                    if cur > prev + 1 and self._moyu_zeroed:  # genuine count after a 0
                        self._moyu_ran = True
                    if cur != prev:
                        self._moyu_stable_t = now
                    # fallback when the timer is left stopped (no reset): record
                    # ONCE, after the value is steady ~1.3 s (decode is reliable
                    # at 48 kHz, so a held value means genuinely stopped)
                    if (ok and self._moyu_ran and not self._moyu_recorded and cur >= 200
                            and (now - self._moyu_stable_t) > 1.3):
                        f = _final()
                        if _commit_ok(f):
                            self._moyu_log(">>> RECORD(hold) %.3f" % (f / 1000.0))
                            self._record(f / 1000.0, None)
                            self._moyu_recorded = True
                        else:
                            self._moyu_log(">>> SKIP(hold) f=%d" % f)

                self._moyu_prevcur = cur
                # No live mirror of the running time on the app screen — it adds
                # GUI churn that can stutter and (via the GIL) hurt the decode.
                # The recorded time appears on the screen when the solve commits.
        except Exception:
            pass
        self.after(50, self._moyu_poll)

    # ── settings ──────────────────────────────────────────────────

    def _open_settings(self):
        if self._settings_win and self._settings_win.winfo_exists():
            _bring_to_front(self._settings_win); return
        self._settings_win = SettingsWindow(
            self, self.cfg, self.sm,
            on_change         = self._apply_settings_debounced,
            on_session_reload = self._session_reload,
        )

    def _open_tools(self):
        if self._tools_win and self._tools_win.winfo_exists():
            _bring_to_front(self._tools_win); return
        self._tools_win = ToolsWindow(self)

    def _session_reload(self):
        self._load_session(self.sm.last)
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.lift()

    def _open_notes(self):
        if self._notes_win and self._notes_win.winfo_exists():
            self._notes_win.lift(); return
        win = ctk.CTkToplevel(self)
        win.title(f"Notatki — {self.cur}")
        win.geometry("440x320")
        win.resizable(True, True)
        win.grab_set()
        self._notes_win = win
        ctk.CTkLabel(win, text=f"Notatki do sesji: {self.cur}",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            padx=16, pady=(14,6), anchor="w")
        tb = ctk.CTkTextbox(win, font=ctk.CTkFont(size=13), wrap="word")
        tb.pack(fill="both", expand=True, padx=16, pady=(0,8))
        tb.insert("1.0", self.sm.get_notes(self.cur))
        def _save():
            self.sm.set_notes(self.cur, tb.get("1.0","end").rstrip("\n"))
            win.destroy()
        bf = ctk.CTkFrame(win, fg_color="transparent")
        bf.pack(padx=16, pady=(0,14), fill="x")
        ctk.CTkButton(bf, text="Zapisz", width=100, command=_save).pack(side="right", padx=(8,0))
        ctk.CTkButton(bf, text="Zamknij", width=100, fg_color="gray25",
                      hover_color="gray35", command=win.destroy).pack(side="right")

    def _export_session(self):
        times = self.sm.get(self.cur)["times"]
        if not times:
            mb.showinfo("Export", "Brak czasów do eksportu.", parent=self); return
        fmt_choice = mb.askyesnocancel(
            "Format eksportu",
            "Tak → CSV\nNie → JSON\nAnuluj → wyjdź",
            parent=self)
        if fmt_choice is None: return
        ext = ".csv" if fmt_choice else ".json"
        path = fd.asksaveasfilename(
            parent=self,
            defaultextension=ext,
            filetypes=[("CSV","*.csv")] if fmt_choice else [("JSON","*.json")],
            initialfile=f"{self.cur}{ext}",
            title="Zapisz eksport")
        if not path: return
        if fmt_choice:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["#","Czas","Kara","Efektywny","Scramble","Data"])
                dec = self.cfg.g("timer","decimals")
                for i, e in enumerate(times, 1):
                    eff = effective(e)
                    eff_s = "DNF" if eff == float("inf") else fmt(eff, dec)
                    w.writerow([i, fmt(e["time"],dec), e.get("penalty",""),
                                eff_s, e.get("scramble",""), e.get("date","")])
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"session": self.cur, "times": times}, f,
                          ensure_ascii=False, indent=2)
        mb.showinfo("Export", f"Zapisano: {path}", parent=self)

    def _rename_current_session(self):
        old = self.cur
        new = sd.askstring("Zmień nazwę sesji", "Nowa nazwa:", initialvalue=old, parent=self)
        if not new or not new.strip(): return
        new = new.strip()
        if new == old: return
        if new in self.sm.names:
            mb.showerror("Błąd", f"Sesja '{new}' już istnieje.", parent=self); return
        self.sm.rename(old, new)
        self.cur = new
        self.session_var.set(new)
        self.session_menu.configure(values=self.sm.names)

    def _toggle_fullscreen(self):
        fs = not self.attributes("-fullscreen")
        self.attributes("-fullscreen", fs)
        self._fs_btn.configure(text="✕" if fs else "⛶")

    def _toggle_focus(self):
        self._focus_mode = not self._focus_mode
        if self._focus_mode:
            self._rp_frame.grid_remove()
            self.stats_card.grid_remove()
            self._focus_btn.configure(fg_color="#4a4a8a")
        else:
            self._rp_frame.grid()
            self.stats_card.grid()
            self._focus_btn.configure(fg_color="gray25")

    def _on_escape(self, event=None):
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)
            self._fs_btn.configure(text="⛶")
        elif self._state == self.INSPECTION:
            self._state = self.IDLE
            self.insp_t = None
            self._insp_pen = None
            self._insp_beeped.clear()
            dec = self.cfg.g("timer", "decimals")
            self.timer_var.set(f"0.{'0'*dec}")
            self._set_timer_color(self.IDLE)
            self.hint_var.set("Przytrzymaj SPACJĘ żeby przygotować start")
        else:
            self._manual_cancel()

    def _toggle_main_viz(self):
        self._main_viz_on = not self._main_viz_on
        self.cfg.s("show_main_viz", self._main_viz_on)
        if self._main_viz_on:
            self._left_viz_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 4), pady=8)
            self._viz_main_btn.configure(fg_color="#4a4a8a")
            self.after(80, self._refresh_main_viz)
        else:
            self._left_viz_frame.grid_forget()
            self._viz_main_btn.configure(fg_color="gray25")

    def _refresh_main_viz(self):
        if not self._main_viz_on:
            return
        canvas = self._left_viz_canvas
        canvas.update_idletasks()
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10:
            self.after(80, self._refresh_main_viz)
            return
        canvas.delete("all")
        scr    = getattr(self, "scramble", "")
        puzzle = self.puzzle_var.get() if hasattr(self, "puzzle_var") else "3x3"
        state  = _make_viz_state(puzzle, scr)
        if state is None:
            canvas.create_text(w//2, h//2, text="Brak wizualizacji",
                               fill="#888888", font=("Segoe UI",11), anchor="center")
            return
        nc, nr = _viz_net_dims(state)
        cell = max(1, min(w // (nc+1), h // (nr+1)))
        x0 = max(0, (w - nc*cell)//2)
        y0 = max(0, (h - nr*cell)//2)
        state.draw_net(canvas, x0, y0, cell)


if __name__ == "__main__":
    App().mainloop()

"""The main App window: timer state machine, UI construction, times list, stats, session/puzzle switching, hardware-timer wiring."""
import ctypes
import os
import time, random, json, csv, copy, zipfile, threading, math
from datetime import datetime
import customtkinter as ctk
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
from ui.tools_window import ToolsWindow, _load_mpl


# Windows: set app ID so taskbar shows custom icon (not generic Python icon)
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "rubiks.timer.app.1"
    )
except Exception:
    pass


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


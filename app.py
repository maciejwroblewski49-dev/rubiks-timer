"""The main App window: timer state machine, movable panels (scramble / timer / stats / times / cube preview), session/puzzle switching, hardware-timer wiring."""
import ctypes
import os
import time, json, csv, threading, math
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
import tkinter.simpledialog as sd
import tkinter.filedialog as fd
import tkinter.messagebox as mb

from utils import fmt, display, effective, _bring_to_front, _HAS_WINSOUND, _winsound
from scramble import PUZZLES
from persistence import ICON_FILE, Config, Sessions
from hardware_timer import MoyuInput, _load_sounddevice, _moyu_mode
from cube_sim import _make_viz_state, _viz_net_dims
from stats import SessionStats
from ui import theme
from ui.theme import C, pick
from ui.layout import LayoutManager, PANELS, PANEL_NAMES, PRESETS, FOCUS_LAYOUT
from ui.times_list import TimesList
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

INF = float("inf")
HINT_IDLE = "Przytrzymaj SPACJĘ żeby przygotować start"

# while a solve is running with "hide UI while solving" on
_SOLVING_LAYOUT = {"timer": {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0, "visible": True}}


class App(ctk.CTk):
    IDLE="idle"; READY="ready"; INSPECTION="inspection"
    RUNNING="running"; STOPPED="stopped"; MANUAL_INPUT="manual_input"

    def __init__(self):
        cfg = Config()
        theme.install(cfg)               # palette for every window, before any widget exists
        super().__init__()
        self.title("Wróbel Timer")
        self.geometry("1180x760")
        self.minsize(900, 600)
        if os.path.exists(ICON_FILE):
            try:
                self.iconbitmap(ICON_FILE)
                self.after(200, lambda: self.iconbitmap(ICON_FILE))
            except Exception:
                pass                     # .ico is Windows-only

        self.cfg   = cfg
        self.sm    = Sessions()
        self.cur   = self.sm.last
        self.stats = SessionStats(self.cfg.g("stats", "trim_mode"))
        self._state = self.IDLE
        self.start_t      = None
        self.insp_t       = None
        self.space_down   = False
        self.scramble     = ""
        self._insp_pen    = None
        self._insp_beeped = set()
        self._settings_win = None
        self._tools_win    = None
        self._detail_win   = None
        self._stat_win     = None
        self._notes_win    = None
        self._scramble_hist: list = []
        self._scramble_idx: int  = -1
        self._manual_buf: str   = ""
        self._streak: int         = 0
        self._focus_mode: bool    = False
        self._solving_view: bool  = False
        self._edit_bar            = None
        self._fit_id              = None
        self._look_key            = None

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
        self.bind("<l>", lambda _: self._toggle_layout_edit())
        self.bind("<L>", lambda _: self._toggle_layout_edit())
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

    # ── small style helpers ───────────────────────────────────────

    def _acc(self):
        return theme.accent(self.cfg)

    def _btn(self, parent, text, command, width=34, primary=False, height=32, size=13, **kw):
        acc = self._acc()
        if primary:
            colors = dict(fg_color=acc,
                          hover_color=(theme.mix(acc[0], "#000000", 0.15),
                                       theme.mix(acc[1], "#000000", 0.2)),
                          text_color="white")
        else:
            colors = dict(fg_color=C["button"], hover_color=C["button_hover"],
                          text_color=C["text"])
        colors.update(kw)
        return ctk.CTkButton(parent, text=text, command=command, width=width,
                             height=height, corner_radius=8,
                             font=theme.font(size), **colors)

    def _menu(self, parent, variable, values, command, width):
        acc = self._acc()
        return ctk.CTkOptionMenu(
            parent, variable=variable, values=values, command=command,
            width=width, height=32, corner_radius=8, font=theme.font(13),
            fg_color=C["button"], button_color=C["button_hover"],
            button_hover_color=acc, text_color=C["text"],
            dropdown_fg_color=C["panel"], dropdown_hover_color=C["button_hover"],
            dropdown_text_color=C["text"], dropdown_font=theme.font(13))

    def _set_active(self, btn, on):
        acc = self._acc()
        if on:
            btn.configure(fg_color=acc, text_color="white")
        else:
            btn.configure(fg_color=C["button"], text_color=C["text"])

    def _scale(self):
        try:
            return ctk.ScalingTracker.get_widget_scaling(self)
        except Exception:
            return 1.0

    # ── build UI ──────────────────────────────────────────────────

    def _build_ui(self):
        self._look_key = (self.cfg.g("accent"), self.cfg.g("layout", "radius"))
        self.configure(fg_color=self.cfg.g("colors", "bg_window") or C["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()

        self._area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._area.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        frames = {pid: self._make_panel() for pid in PANELS}
        self._panels = frames
        self._build_scramble_panel(frames["scramble"])
        self._build_timer_panel(frames["timer"])
        self._build_stats_panel(frames["stats"])
        self._build_times_panel(frames["times"])
        self._build_viz_panel(frames["viz"])

        self.layout = LayoutManager(self, self._area, frames)
        self.layout.set_editing(False)
        self.layout.apply()

    def _make_panel(self):
        return ctk.CTkFrame(self._area, fg_color=C["panel"],
                            corner_radius=int(self.cfg.g("layout", "radius")),
                            border_width=1 if self.cfg.g("layout", "borders") else 0,
                            border_color=C["border"])

    def _build_header(self):
        hdr = ctk.CTkFrame(self, corner_radius=0, height=58,
                           fg_color=self.cfg.g("colors", "bg_header") or C["header"])
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_rowconfigure(0, weight=1)
        self._hdr_frame = hdr
        acc = self._acc()

        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.grid(row=0, column=0, padx=(16, 8), sticky="w")
        ctk.CTkLabel(logo, text="⏱", width=34, height=34, corner_radius=10,
                     fg_color=acc, text_color="white",
                     font=theme.font(17, "bold")).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(logo, text="Wróbel Timer", text_color=C["text"],
                     font=theme.font(18, "bold")).pack(side="left")
        self._logo = logo

        bar = ctk.CTkFrame(hdr, fg_color="transparent")
        bar.grid(row=0, column=1, padx=8, sticky="w")
        self.puzzle_var = ctk.StringVar()
        self._menu(bar, self.puzzle_var, list(PUZZLES), self._on_puzzle, 104).pack(side="left", padx=(0, 6))
        self.session_var = ctk.StringVar()
        self.session_menu = self._menu(bar, self.session_var, self.sm.names, self._on_session, 190)
        self.session_menu.pack(side="left", padx=(0, 4))
        self.session_menu.bind("<Double-Button-1>", lambda e: self._rename_current_session())
        self._btn(bar, "✏", self._rename_current_session).pack(side="left", padx=2)
        self._btn(bar, "📝", self._open_notes).pack(side="left", padx=2)
        self._btn(bar, "＋", self._new_session, size=15).pack(side="left", padx=2)

        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.grid(row=0, column=2, padx=(8, 14), sticky="e")
        self._btn(right, "📈  Narzędzia", self._open_tools, width=118).pack(side="left", padx=3)
        self._layout_btn = self._btn(right, "✥  Układ", self._toggle_layout_edit, width=92)
        self._layout_btn.pack(side="left", padx=3)
        self._btn(right, "⚙", self._open_settings, size=15).pack(side="left", padx=3)
        self._focus_btn = self._btn(right, "◉", self._toggle_focus, size=15)
        self._focus_btn.pack(side="left", padx=3)
        self._fs_btn = self._btn(right, "⛶", self._toggle_fullscreen, size=15)
        self._fs_btn.pack(side="left", padx=(3, 0))

        # narrow window: drop the logo text before the buttons get squeezed
        def _on_hdr(e):
            want = e.width >= 1060 * self._scale()
            if want and not logo.winfo_ismapped():
                logo.grid()
            elif not want and logo.winfo_ismapped():
                logo.grid_remove()
        hdr.bind("<Configure>", _on_hdr)

    # ── panels ────────────────────────────────────────────────────

    def _build_scramble_panel(self, f):
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
        self._scr_caption = ctk.CTkLabel(top, text="SCRAMBLE", text_color=C["muted"],
                                         font=theme.font(11, "bold"))
        self._scr_caption.pack(side="left")
        small = dict(width=30, height=26, size=12)
        self._viz_main_btn = self._btn(top, "🎲", self._toggle_main_viz, **small)
        self._viz_main_btn.pack(side="right", padx=(3, 0))
        self._btn(top, "⧉", self._copy_scramble, **small).pack(side="right", padx=3)
        self._btn_next_scr = self._btn(top, "▶", self._next_scramble, **small)
        self._btn_next_scr.pack(side="right", padx=3)
        self._btn_prev_scr = self._btn(top, "◀", self._prev_scramble, **small)
        self._btn_prev_scr.pack(side="right", padx=3)

        self.scramble_var = ctk.StringVar()
        self.scramble_lbl = ctk.CTkLabel(f, textvariable=self.scramble_var,
                                         font=theme.font(15, "bold"), justify="center")
        self.scramble_lbl.grid(row=1, column=0, sticky="nsew", padx=14, pady=(2, 10))

        def _wrap(e):
            w = max(100, e.width - int(36 * self._scale()))
            if self.scramble_lbl.cget("wraplength") != w:
                self.scramble_lbl.configure(wraplength=w)
        f.bind("<Configure>", _wrap, add="+")

    def _build_timer_panel(self, f):
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)

        hrow = ctk.CTkFrame(f, fg_color="transparent")
        hrow.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
        self.hint_var = ctk.StringVar(value=HINT_IDLE)
        ctk.CTkLabel(hrow, textvariable=self.hint_var, text_color=C["muted"],
                     font=theme.font(12)).pack(side="left")
        self._insp_on = ctk.BooleanVar(value=self.cfg.g("timer", "inspection_enabled"))
        ctk.CTkSwitch(hrow, text="Inspekcja", variable=self._insp_on, font=theme.font(12),
                      text_color=C["muted"], progress_color=self._acc(),
                      switch_width=34, switch_height=16,
                      command=lambda: self.cfg.s("timer", "inspection_enabled",
                                                 self._insp_on.get())).pack(side="right")

        self.timer_var = ctk.StringVar(value="0.000")
        self._timer_font = theme.font(88, "bold")
        self.timer_lbl = ctk.CTkLabel(f, textvariable=self.timer_var, font=self._timer_font,
                                      text_color=C["text"])
        self.timer_lbl.grid(row=1, column=0, sticky="nsew", padx=8)

        self._target_lbl = ctk.CTkLabel(f, text="", font=theme.font(15, "bold"))
        self._target_lbl.grid(row=2, column=0, pady=(0, 2))

        # fixed-height row so the timer doesn't jump when the buttons appear
        self.pen_frame = ctk.CTkFrame(f, fg_color="transparent", height=44)
        self.pen_frame.grid(row=3, column=0, pady=(0, 10))
        self._pen_inner = ctk.CTkFrame(self.pen_frame, fg_color="transparent")
        self._pen_btns = {}
        for p in ["+2", "DNF", "DNS"]:
            b = self._btn(self._pen_inner, p, lambda x=p: self._pen_click(x),
                          width=76, height=32, size=13)
            b.configure(font=theme.font(13, "bold"))
            b.pack(side="left", padx=5)
            self._pen_btns[p] = b
        ctk.CTkLabel(self.pen_frame, text="", width=1, height=40).pack()
        self._show_pens(False)

        f.bind("<Configure>", lambda e: self._schedule_fit(), add="+")

    def _show_pens(self, on):
        if on:
            self._pen_inner.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self._pen_inner.place_forget()

    def _build_stats_panel(self, f):
        self._stats_body = ctk.CTkFrame(f, fg_color="transparent")
        self._stats_body.pack(fill="both", expand=True, padx=8, pady=8)
        self._stats_cols = None
        self.stat_lbl = {}
        self._stat_tiles = []
        self._rebuild_stats()
        self._stats_body.bind("<Configure>", lambda e: self._regrid_stats(), add="+")

    def _build_times_panel(self, f):
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(top, text="Czasy", text_color=C["text"],
                     font=theme.font(14, "bold")).pack(side="left")
        self._count_lbl = ctk.CTkLabel(top, text="", text_color=C["muted"], font=theme.font(12))
        self._count_lbl.pack(side="left", padx=(8, 0))
        small = dict(height=26, size=12)
        self._btn(top, "⌨ Wpisz", self._manual_time, width=74, **small).pack(side="right")
        self._btn(top, "💾", self._export_session, width=30, **small).pack(side="right", padx=4)
        self.times_list = TimesList(f, self, on_click=self._show_detail, on_context=self._ctx)
        self.times_list.pack(fill="both", expand=True, padx=(6, 6), pady=(0, 8))

    def _build_viz_panel(self, f):
        r = max(6, int(self.cfg.g("layout", "radius")) // 2)
        self._viz_canvas = tk.Canvas(f, highlightthickness=0, bd=0, bg=pick(C["panel"]))
        self._viz_canvas.pack(fill="both", expand=True, padx=r, pady=r)
        self._viz_canvas.bind("<Configure>", lambda e: self._refresh_main_viz())

    # ── stats tiles ───────────────────────────────────────────────

    def _stat_defs(self):
        defs = []
        g = lambda k: self.cfg.g("stats", k)
        if g("show_best"):  defs.append(("Najlepszy", "best"))
        if g("show_ao5"):   defs.append(("Ao5", "ao5"))
        if g("show_ao12"):  defs.append(("Ao12", "ao12"))
        if g("show_ao100"): defs.append(("Ao100", "ao100"))
        if g("show_mean"):  defs.append(("Średnia", "mean"))
        for n in g("custom_averages"):
            defs.append((f"Ao{n}", f"_cao_{n}"))
        defs.append(("Solvy", "count"))
        return defs

    def _rebuild_stats(self):
        for w in self._stats_body.winfo_children():
            w.destroy()
        self.stat_lbl.clear()
        self._stat_tiles = []
        self._stats_cols = None
        acc = self._acc()
        for title, key in self._stat_defs():
            tile = ctk.CTkFrame(self._stats_body, fg_color=C["panel_alt"], corner_radius=10)
            inner = ctk.CTkFrame(tile, fg_color="transparent")
            inner.pack(expand=True, fill="x", padx=2)      # vertically centred
            ctk.CTkLabel(inner, text=title.upper(), text_color=C["muted"],
                         font=theme.font(10, "bold"), height=16).pack(pady=(6, 0))
            clickable = key != "count"
            val = ctk.CTkButton(inner, text="—", font=theme.font(20, "bold"),
                                fg_color="transparent", text_color=C["text"],
                                hover_color=theme.tint(acc, "panel_alt", 0.18) if clickable else C["panel_alt"],
                                height=30, corner_radius=8,
                                cursor="hand2" if clickable else "arrow",
                                command=(lambda k=key: self._show_stat_detail(k)) if clickable else None)
            val.pack(fill="x", padx=6)
            sub = ctk.CTkLabel(inner, text="", text_color=C["muted"], font=theme.font(11),
                               height=16, cursor="hand2" if key.startswith(("ao", "_cao_")) else "arrow")
            sub.pack(pady=(0, 6))
            if key.startswith(("ao", "_cao_")):
                n = int(key[2:]) if key.startswith("ao") else int(key[5:])
                sub.bind("<Button-1>", lambda e, n=n: self._show_stat_detail(f"_best_{n}"))
            self.stat_lbl[key] = (val, sub)
            self._stat_tiles.append(tile)
        self._regrid_stats()

    def _regrid_stats(self):
        tiles = self._stat_tiles
        if not tiles:
            return
        W = self._stats_body.winfo_width()
        if W < 20:
            self.after(50, self._regrid_stats)
            return
        min_w = 112 * self._scale()
        cols = max(1, min(len(tiles), int(W // min_w)))
        if cols == self._stats_cols:
            return
        self._stats_cols = cols
        rows = math.ceil(len(tiles) / cols)
        body = self._stats_body
        for c in range(len(tiles) + 1):
            body.grid_columnconfigure(c, weight=1 if c < cols else 0, uniform="st" if c < cols else "")
        for r in range(len(tiles) + 1):
            body.grid_rowconfigure(r, weight=1 if r < rows else 0)
        for k, t in enumerate(tiles):
            t.grid(row=k // cols, column=k % cols, sticky="nsew", padx=3, pady=3)

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

        # accent / corner radius are baked into many widgets: rebuild once
        look = (self.cfg.g("accent"), self.cfg.g("layout", "radius"))
        if look != self._look_key:
            self._rebuild_ui()
            return

        family = self.cfg.g("font", "timer_family")
        self._timer_font.configure(family=family if family and family != "Default"
                                   else theme.ui_family())
        self._fit_timer_font()

        sc_sz     = self.cfg.g("font", "scramble_size")
        sc_col    = self.cfg.g("colors", "scramble")
        sc_family = self.cfg.g("font", "scramble_family")
        align     = self.cfg.g("scramble_align")
        sc_anchor = {"left": "w", "center": "center", "right": "e"}.get(align, "center")
        if sc_col.upper() == "#DDDDDD":          # the default = follow the theme
            sc_col = C["text"]
        self.scramble_lbl.configure(
            font=theme.font(sc_sz, "bold",
                            sc_family if sc_family and sc_family != "Default" else None),
            text_color=sc_col, justify=align, anchor=sc_anchor)

        self._insp_on.set(self.cfg.g("timer", "inspection_enabled"))
        self._set_timer_color(self._state)

        self.stats.set_mode(self.cfg.g("stats", "trim_mode"))
        # _rebuild_stats tylko gdy konfiguracja statystyk się zmieniła
        stats_key = str(self.cfg.g("stats"))
        if getattr(self, "_last_stats_cfg", None) != stats_key:
            self._rebuild_stats()
            self._last_stats_cfg = stats_key
        self._update_stats()

        self.configure(fg_color=self.cfg.g("colors", "bg_window") or C["bg"])
        self._hdr_frame.configure(fg_color=self.cfg.g("colors", "bg_header") or C["header"])
        if not self.layout.editing:
            self.layout.set_editing(False)       # re-applies panel borders
        self.layout.apply()
        self._viz_canvas.configure(bg=pick(C["panel"]))
        self.times_list.redraw()
        self._refresh_main_viz()

    def _rebuild_ui(self):
        """Tear down and rebuild the main window (accent / radius change)."""
        if self._edit_bar is not None:
            self._edit_bar.destroy(); self._edit_bar = None
        for w in self.winfo_children():
            if isinstance(w, tk.Toplevel):
                continue
            w.destroy()
        self._last_stats_cfg = None
        theme.install(self.cfg)
        self._build_ui()
        self._load_session(self.cur, keep_scramble=True)
        self._apply_settings()

    def _set_timer_color(self, state):
        pen_active = False
        if state == self.STOPPED:
            times = self.sm.get(self.cur)["times"]
            if times and times[-1].get("penalty") in ("DNF","DNS"):
                pen_active = True
        if pen_active:
            col = self.cfg.g("colors","timer_penalty")
        elif state == self.READY:
            col = self.cfg.g("colors","timer_ready")
        elif state == self.INSPECTION:
            col = self.cfg.g("colors","timer_inspection")
        elif state == self.RUNNING:
            col = self.cfg.g("colors","timer_running")
        elif state == self.MANUAL_INPUT:
            col = self._acc()
        else:
            col = self.cfg.g("colors","timer_idle")
            if col.upper() == "#FFFFFF":          # the default = follow the theme
                col = C["text"]
        self.timer_lbl.configure(text_color=col)

    def _schedule_fit(self):
        if self._fit_id is not None:
            self.after_cancel(self._fit_id)
        self._fit_id = self.after(40, self._fit_timer_font)

    def _fit_timer_font(self):
        self._fit_id = None
        if not self.cfg.g("timer", "autosize"):
            size = int(self.cfg.g("font", "timer_size"))
        else:
            f = self._panels["timer"]
            W, H = f.winfo_width(), f.winfo_height()
            if W < 50 or H < 50:
                return
            s = self._scale()
            chars = len(fmt(59.999, self.cfg.g("timer", "decimals"))) + 0.4
            by_w = (W - 40 * s) / (chars * 0.62)
            by_h = (H - 120 * s) * 0.95
            size = int(max(28, min(by_w, by_h, 340 * s)) / s)
        if self._timer_font.cget("size") != size:
            self._timer_font.configure(size=size)

    def _on_layout_changed(self):
        self._set_active(self._viz_main_btn, self.layout.visible("viz"))
        if self._edit_bar is not None:
            self._edit_bar.lift()
            self._edit_preset_var.set(self.cfg.g("layout", "preset"))
        self._schedule_fit()

    # ── session ───────────────────────────────────────────────────

    def _load_session(self, name, keep_scramble=False):
        self.cur = name
        sess = self.sm.get(name)
        self.session_var.set(name)
        self.session_menu.configure(values=self.sm.names)
        self.puzzle_var.set(sess["puzzle"])
        self._scr_caption.configure(text=f"SCRAMBLE  ·  {sess['puzzle']}")

        # the list is virtual and the stats are incremental, so even a session
        # with tens of thousands of solves opens instantly
        self.stats.set_mode(self.cfg.g("stats", "trim_mode"))
        self.stats.load(sess["times"])
        self.times_list.scroll_to_top()
        self._update_stats()
        if keep_scramble and self.scramble:
            self._show_scramble(self.scramble)
        else:
            self._scramble_hist.clear()
            self._scramble_idx = -1
            self._new_scramble()

    def _on_session(self, name):
        self.sm.switch(name); self._load_session(name)

    def _on_puzzle(self, puzzle):
        self.sm.set_puzzle(self.cur, puzzle)
        self._scr_caption.configure(text=f"SCRAMBLE  ·  {puzzle}")
        self._new_scramble()

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
        self._btn_prev_scr.configure(state="normal" if can_prev else "disabled")

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

    def _copy_scramble(self):
        self.clipboard_clear()
        self.clipboard_append(self.scramble)
        self._flash_hint("Scramble skopiowany do schowka")

    def _flash_hint(self, text, ms=1600):
        self.hint_var.set(text)
        def _back():
            if self.hint_var.get() == text and self._state in (self.IDLE, self.STOPPED):
                self.hint_var.set(HINT_IDLE)
        self.after(ms, _back)

    # ── tick ──────────────────────────────────────────────────────

    def _tick(self):
        if self._state == self.INSPECTION:
            elapsed = time.perf_counter() - self.insp_t
            rem = self.cfg.g("timer","inspection_duration") - elapsed
            if rem > 0:
                self.timer_var.set(str(int(rem)+1))
            elif rem > -2:
                if self.timer_var.get() != "+2":
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
        if self.layout.editing: return

        if self._state == self.MANUAL_INPUT:
            self._manual_cancel()

        if self._state in (self.IDLE, self.STOPPED):
            self._state = self.READY
            self._set_timer_color(self.READY)
            self.hint_var.set("Puść SPACJĘ żeby wystartować")
            self._show_pens(False)

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
            self._set_solving_view(True)
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
        self._set_solving_view(True)

    def _set_solving_view(self, on):
        """Optionally hide every panel except the timer while solving."""
        on = bool(on) and self.cfg.g("timer", "hide_ui_while_solving")
        if on == self._solving_view:
            return
        self._solving_view = on
        if on:
            self.layout.override = _SOLVING_LAYOUT
        else:
            self.layout.override = FOCUS_LAYOUT if self._focus_mode else None
        self.layout.apply()

    # ── recording ─────────────────────────────────────────────────

    def _record(self, t, penalty):
        dec   = self.cfg.g("timer","decimals")
        st    = self.stats
        prev_best = st.best if st.best is not None else INF
        watch = [n for n in (5, 12, 100) if self.cfg.g("stats", f"show_ao{n}")]
        prev_avg = {n: st.best_average(n)[0] for n in watch}

        entry = {"time":t, "penalty":penalty, "scramble":self.scramble,
                 "puzzle": self.puzzle_var.get(),
                 "date":datetime.now().isoformat()}
        self.sm.add(self.cur, entry)
        st.append(entry)
        self._set_solving_view(False)
        self.timer_var.set(display(entry, dec))
        new_eff = effective(entry)
        is_pb = new_eff != INF and new_eff < prev_best and st.count > 1

        if is_pb:
            self.timer_lbl.configure(text_color=pick(C["gold"]))
            self.after(1800, lambda: self._set_timer_color(self.STOPPED))
            if self.cfg.g("target","pb_sound") and _HAS_WINSOUND:
                threading.Thread(target=self._play_pb_sound, daemon=True).start()
        else:
            self._set_timer_color(self.STOPPED)

        msgs = []
        if is_pb:
            msgs.append(("🏆 Nowy PB!", C["gold"]))
        for n in watch:
            v, idx = st.best_average(n)
            if idx == st.count - 1 and prev_avg[n] is not None and v < prev_avg[n]:
                msgs.append((f"🏆 PB ao{n}", C["gold"]))

        # ── target / streak ──
        tgt_en  = self.cfg.g("target","enabled")
        tgt_val = self.cfg.g("target","time")
        if tgt_en and new_eff != INF:
            if new_eff <= tgt_val:
                self._streak += 1
                msgs.insert(0, (f"✓ -{tgt_val - new_eff:.2f}s  streak {self._streak}", C["good"]))
            else:
                self._streak = 0
                msgs.insert(0, (f"✗ +{new_eff - tgt_val:.2f}s  sub-{tgt_val:.1f}", C["bad"]))
        if msgs:
            self._target_lbl.configure(text="   ·   ".join(m for m, _ in msgs),
                                       text_color=msgs[0][1])
        else:
            self._target_lbl.configure(text="")

        self.hint_var.set(HINT_IDLE)
        self.times_list.on_append()
        self._refresh_pen_buttons(penalty)
        self._show_pens(True)
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
            self._set_active(b, p == active)

    def _pen_click(self, pen):
        times = self.sm.get(self.cur)["times"]
        if not times: return
        self._set_pen(len(times) - 1, pen, show=True)

    def _set_pen(self, idx, pen, show=False):
        times = self.sm.get(self.cur)["times"]
        if not (0 <= idx < len(times)): return
        entry = dict(times[idx])
        entry["penalty"] = None if entry.get("penalty")==pen else pen
        self.sm.update(self.cur, idx, entry)
        self.stats.update(idx, entry)
        dec = self.cfg.g("timer","decimals")
        if idx == len(times)-1 and (show or self._state == self.STOPPED):
            self.timer_var.set(display(entry, dec))
            self._set_timer_color(self.STOPPED)
            self._refresh_pen_buttons(entry["penalty"])
        self.times_list.redraw()
        self._update_stats()
        if self._tools_win and self._tools_win.winfo_exists():
            self._tools_win.refresh_after_solve()

    # ── times list ────────────────────────────────────────────────

    def _ctx(self, event, idx):
        times = self.sm.get(self.cur)["times"]
        if idx >= len(times): return
        entry = times[idx]
        m = tk.Menu(self, tearoff=0)
        m.add_command(label=f"Solv #{idx + 1}  —  szczegóły", command=lambda i=idx: self._show_detail(i))
        m.add_separator()
        for pen in ["+2","DNF","DNS"]:
            chk = "✓  " if entry.get("penalty")==pen else "      "
            m.add_command(label=f"{chk}{pen}",
                          command=lambda p=pen, i=idx: self._set_pen(i,p))
        m.add_separator()
        def _copy(s=entry.get("scramble", "")):
            self.clipboard_clear(); self.clipboard_append(s)
        m.add_command(label="Kopiuj scramble", command=_copy)
        m.add_command(label="Usuń", command=lambda i=idx: self._del_time(i))
        m.tk_popup(event.x_root, event.y_root)

    def _show_detail(self, idx):
        if self._detail_win and self._detail_win.winfo_exists():
            self._detail_win.destroy()
        self._detail_win = TimeDetailDialog(self, idx)

    def _show_stat_detail(self, key):
        if self._stat_win is not None and self._stat_win.winfo_exists():
            self._stat_win.destroy()
        self._stat_win = StatDetailDialog(self, key)

    def _del_time(self, idx):
        if self._detail_win and self._detail_win.winfo_exists():
            self._detail_win.destroy()
        self._detail_win = None
        if self._stat_win and self._stat_win.winfo_exists():
            self._stat_win.destroy()
        self._stat_win = None
        self.sm.delete(self.cur, idx)
        self.stats.delete(idx)
        self.times_list.redraw()
        self._update_stats()
        if self._tools_win and self._tools_win.winfo_exists():
            self._tools_win.refresh_after_solve()

    # ── stats ─────────────────────────────────────────────────────

    def _fs(self, v):
        if v is None: return "—"
        if v == INF:  return "DNF"
        return fmt(v, self.cfg.g("timer", "decimals"))

    def _update_stats(self):
        times = self.sm.get(self.cur)["times"]
        st = self.stats
        if st.count != len(times):            # something edited the list behind our back
            st.load(times)
        show_best_avg = self.cfg.g("stats", "show_best_avg")

        for key, (val, sub) in self.stat_lbl.items():
            sub_txt = ""
            if key == "count":
                v_txt = str(st.count)
                sub_txt = f"{st.dnf_count} DNF" if st.dnf_count else ""
            elif key == "best":
                v_txt = self._fs(st.best)
                if st.worst is not None and st.valid_count > 1:
                    sub_txt = f"najgorszy {self._fs(st.worst)}"
            elif key == "mean":
                v_txt = self._fs(st.mean)
                if st.std is not None:
                    sub_txt = f"σ {self._fs(st.std)}"
            else:
                n = int(key[2:]) if key.startswith("ao") else int(key[5:])
                v_txt = self._fs(st.current(n))
                if show_best_avg:
                    b, _ = st.best_average(n)
                    if b is not None:
                        sub_txt = f"PB {self._fs(b)}"
            if val.cget("text") != v_txt:
                val.configure(text=v_txt)
            if sub.cget("text") != sub_txt:
                sub.configure(text=sub_txt)
        n = st.count
        self._count_lbl.configure(text=f"{n}" if n else "")

    # ── manual time entry ─────────────────────────────────────────

    def _manual_time(self):
        if self._state in (self.RUNNING, self.MANUAL_INPUT, self.INSPECTION):
            return
        self._state = self.MANUAL_INPUT
        self._manual_buf = ""
        self.timer_var.set("0.00")
        self._set_timer_color(self.MANUAL_INPUT)
        self.hint_var.set("Wpisz czas (np. 1233 = 12.33s)  •  ← cofnij  •  Enter = OK  •  Esc = anuluj")
        self._show_pens(False)

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
        entry = {
            "time":    t,
            "penalty": None,
            "scramble": self.scramble,
            "puzzle":  self.puzzle_var.get(),
            "date":    datetime.now().isoformat(),
            "manual":  True,
        }
        self.sm.add(self.cur, entry)
        self.stats.append(entry)
        self.times_list.on_append()
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
        self.hint_var.set(HINT_IDLE)

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
                    eff_s = "DNF" if eff == INF else fmt(eff, dec)
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
        if self.layout.editing:
            return
        self._focus_mode = not self._focus_mode
        if not self._solving_view:
            self.layout.override = FOCUS_LAYOUT if self._focus_mode else None
            self.layout.apply()
        self._set_active(self._focus_btn, self._focus_mode)

    # ── layout editing ────────────────────────────────────────────

    def _toggle_layout_edit(self):
        if self._state in (self.READY, self.INSPECTION, self.RUNNING, self.MANUAL_INPUT):
            return
        if self._focus_mode:
            self._toggle_focus()
        on = not self.layout.editing
        self.layout.set_editing(on)
        self._set_active(self._layout_btn, on)
        if on:
            self._show_edit_bar()
        elif self._edit_bar is not None:
            self._edit_bar.destroy(); self._edit_bar = None
        self.layout.apply()

    def _show_edit_bar(self):
        acc = self._acc()
        bar = ctk.CTkFrame(self._area, fg_color=C["header"], corner_radius=14,
                           border_width=2, border_color=acc)
        ctk.CTkLabel(bar, text="✥  Przeciągnij belkę panelu, żeby go przesunąć  ·  róg ◢ zmienia rozmiar",
                     text_color=C["text"], font=theme.font(12)).pack(side="left", padx=(14, 12), pady=10)
        pv = ctk.StringVar(value=self.cfg.g("layout", "preset"))
        self._edit_preset_var = pv
        def _preset(name):
            self.layout.load_preset(name)
        self._menu(bar, pv, list(PRESETS), _preset, 160).pack(side="left", padx=4)

        def _panels_menu():
            m = tk.Menu(self, tearoff=0)
            self._panel_vars = []      # keep the BooleanVars alive while the menu is open
            for pid in PANELS:
                var = tk.BooleanVar(value=self.layout.visible(pid))
                self._panel_vars.append(var)
                m.add_checkbutton(label=PANEL_NAMES[pid], variable=var,
                                  command=lambda p=pid, v=var: self.layout.set_visible(p, v.get()))
            x = pb.winfo_rootx(); y = pb.winfo_rooty() - 6
            m.tk_popup(x, y - 26 * len(PANELS))
        pb = self._btn(bar, "Panele ▾", _panels_menu, width=92)
        pb.pack(side="left", padx=4)

        sv = ctk.BooleanVar(value=self.cfg.g("layout", "snap"))
        ctk.CTkSwitch(bar, text="Przyciąganie", variable=sv, font=theme.font(12),
                      text_color=C["text"], progress_color=acc,
                      command=lambda: self.cfg.s("layout", "snap", sv.get())).pack(side="left", padx=10)
        self._btn(bar, "Gotowe", self._toggle_layout_edit, width=90, primary=True).pack(side="left", padx=(4, 10))
        bar.place(relx=0.5, rely=1.0, y=-14, anchor="s")
        self._edit_bar = bar

    def _on_escape(self, event=None):
        if self.layout.editing:
            self._toggle_layout_edit()
        elif self.attributes("-fullscreen"):
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
            self.hint_var.set(HINT_IDLE)
            self._set_solving_view(False)
        else:
            self._manual_cancel()

    # ── cube preview ──────────────────────────────────────────────

    def _toggle_main_viz(self):
        if self._state in (self.MANUAL_INPUT,):
            return
        self.layout.set_visible("viz", not self.layout.visible("viz"))
        self.after(60, self._refresh_main_viz)

    def _refresh_main_viz(self):
        if not self.layout.visible("viz"):
            return
        canvas = self._viz_canvas
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10:
            return
        canvas.delete("all")
        scr    = getattr(self, "scramble", "")
        puzzle = self.puzzle_var.get() if hasattr(self, "puzzle_var") else "3x3"
        state  = _make_viz_state(puzzle, scr)
        if state is None:
            canvas.create_text(w//2, h//2, text=f"Brak podglądu\ndla {puzzle}",
                               fill=pick(C["muted"]), font=(theme.ui_family(), 11),
                               anchor="center", justify="center")
            return
        nc, nr = _viz_net_dims(state)
        cell = max(1, min(w // (nc+1), h // (nr+1)))
        x0 = max(0, (w - nc*cell)//2)
        y0 = max(0, (h - nr*cell)//2)
        state.draw_net(canvas, x0, y0, cell)

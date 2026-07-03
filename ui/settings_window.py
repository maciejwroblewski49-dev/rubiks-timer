"""Settings window: appearance, timer, hardware-timer audio, stats, data import/export/backup tabs."""
import os, json, csv, zipfile
from datetime import datetime
import customtkinter as ctk
import tkinter.colorchooser as cc
import tkinter.filedialog as fd
import tkinter.messagebox as mb

from utils import _bring_to_front, fmt
from persistence import Config, Sessions, DATA_FILE, CFG_FILE, DATA_DIR
from hardware_timer import MoyuInput


FONT_FAMILIES = [
    "Default",
    # Sans-serif
    "Segoe UI", "Arial", "Arial Black", "Arial Narrow", "Helvetica",
    "Verdana", "Tahoma", "Calibri", "Trebuchet MS", "Century Gothic",
    "Franklin Gothic Medium", "Gill Sans MT", "Microsoft Sans Serif",
    "Lucida Sans", "Segoe Print", "Segoe Script", "Dubai",
    # Serif
    "Georgia", "Times New Roman", "Garamond", "Book Antiqua",
    "Bookman Old Style", "Cambria", "Palatino Linotype",
    "Perpetua", "Sylfaen", "Century",
    # Monospace
    "Consolas", "Courier New", "Lucida Console", "Courier",
    "MS Gothic",
    # Display / Decorative
    "Impact", "Haettenschweiler", "Wide Latin", "Stencil",
    "Broadway", "Playbill", "Rockwell", "Cooper Black",
    "Bauhaus 93", "Berlin Sans FB", "Copperplate Gothic Bold",
    "Script MT Bold", "Monotype Corsiva", "Mistral",
    "Lucida Handwriting", "Ink Free", "Freestyle Script",
    "Jokerman", "Papyrus", "Comic Sans MS", "Forte",
]


COLOR_PRESETS = {
    "WCA Dark (domyślny)": {
        "timer_idle": "#FFFFFF", "timer_ready": "#FF4444",
        "timer_running": "#44DD77", "timer_inspection": "#FFAA00",
        "timer_penalty": "#FF4444", "scramble": "#DDDDDD",
        "bg_window": "", "bg_header": "",
    },
    "Ocean": {
        "timer_idle": "#B0E0FF", "timer_ready": "#FF6B6B",
        "timer_running": "#00D4FF", "timer_inspection": "#FFD700",
        "timer_penalty": "#FF6B6B", "scramble": "#87CEEB",
        "bg_window": "#0a1628", "bg_header": "#0d2440",
    },
    "Neon": {
        "timer_idle": "#00FF88", "timer_ready": "#FF0055",
        "timer_running": "#00FFFF", "timer_inspection": "#FF8800",
        "timer_penalty": "#FF0055", "scramble": "#AAFFAA",
        "bg_window": "#050505", "bg_header": "#0a0a0a",
    },
    "Nord": {
        "timer_idle": "#ECEFF4", "timer_ready": "#BF616A",
        "timer_running": "#A3BE8C", "timer_inspection": "#EBCB8B",
        "timer_penalty": "#BF616A", "scramble": "#D8DEE9",
        "bg_window": "#2e3440", "bg_header": "#3b4252",
    },
    "Solarized": {
        "timer_idle": "#FDF6E3", "timer_ready": "#DC322F",
        "timer_running": "#859900", "timer_inspection": "#B58900",
        "timer_penalty": "#DC322F", "scramble": "#93A1A1",
        "bg_window": "#002b36", "bg_header": "#073642",
    },
    "Sunset": {
        "timer_idle": "#FFE4B5", "timer_ready": "#FF4500",
        "timer_running": "#FF8C00", "timer_inspection": "#FFD700",
        "timer_penalty": "#FF4500", "scramble": "#FFDAB9",
        "bg_window": "#1a0800", "bg_header": "#2a1200",
    },
    "Fiolet": {
        "timer_idle": "#E8D5F5", "timer_ready": "#E91E8C",
        "timer_running": "#9C27B0", "timer_inspection": "#FF9800",
        "timer_penalty": "#E91E8C", "scramble": "#CE93D8",
        "bg_window": "#12001e", "bg_header": "#1e0030",
    },
    "Matrix": {
        "timer_idle": "#00FF41", "timer_ready": "#FF0000",
        "timer_running": "#39FF14", "timer_inspection": "#FFFF00",
        "timer_penalty": "#FF0000", "scramble": "#00CC33",
        "bg_window": "#001100", "bg_header": "#002200",
    },
    "Pastel": {
        "timer_idle": "#FFD6E0", "timer_ready": "#FF8FAB",
        "timer_running": "#B5EAD7", "timer_inspection": "#FFDAC1",
        "timer_penalty": "#FF8FAB", "scramble": "#C7CEEA",
        "bg_window": "#fff0f5", "bg_header": "#ffe0ec",
    },
    "Monochrome": {
        "timer_idle": "#FFFFFF", "timer_ready": "#BBBBBB",
        "timer_running": "#FFFFFF", "timer_inspection": "#DDDDDD",
        "timer_penalty": "#BBBBBB", "scramble": "#AAAAAA",
        "bg_window": "#111111", "bg_header": "#1c1c1c",
    },
}


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, cfg: Config, sm: Sessions, on_change, on_session_reload):
        super().__init__(parent)
        self.title("Ustawienia")
        self.geometry("620x560")
        self.resizable(False, False)
        self.cfg = cfg
        self.sm  = sm
        self.on_change        = on_change
        self.on_session_reload = on_session_reload
        self._build()
        _bring_to_front(self)

    def _build(self):
        tabs = ctk.CTkTabview(self, anchor="nw")
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
        for t in ["🎨  Wygląd", "⏱  Timer", "🔌  Timer audio", "📊  Statystyki", "💾  Dane"]:
            tabs.add(t)
        self._tab_appearance(tabs.tab("🎨  Wygląd"))
        self._tab_timer(tabs.tab("⏱  Timer"))
        self._tab_moyu(tabs.tab("🔌  Timer audio"))
        self._tab_stats(tabs.tab("📊  Statystyki"))
        self._tab_data(tabs.tab("💾  Dane"))

    # ── Timer audio (MoYu / StackMat przez jack) ──────────────────

    def _tab_moyu(self, tab):
        sf = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sf.pack(fill="both", expand=True)
        ctk.CTkLabel(sf, text="Timer audio (MoYu / StackMat Gen3/4/5) — przez jack",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=14, pady=(12, 2))
        if not MoyuInput.available():
            ctk.CTkLabel(sf, text="Biblioteka audio (sounddevice) niedostępna w tej wersji programu.",
                         text_color="#f66").pack(anchor="w", padx=14, pady=8)
            return
        ctk.CTkLabel(sf, text="Podłącz timer jackiem do wejścia mikrofonowego, wybierz TYP i urządzenie, włącz.\n"
                              "Czasy zapisują się automatycznie po każdym solve (jeden czas na solve).",
                     font=ctk.CTkFont(size=11), text_color="gray60", justify="left").pack(anchor="w", padx=14)

        en_var = ctk.BooleanVar(value=self.cfg.g("moyu", "enabled"))

        ctk.CTkLabel(sf, text="Typ timera:", anchor="w").pack(anchor="w", padx=14, pady=(12, 0))
        type_map = {"MoYu": "m", "StackMat (Gen3/4/5)": "s"}
        rev_map  = {v: k for k, v in type_map.items()}
        cur_type = self.cfg.g("moyu", "type") or "m"
        type_var = ctk.StringVar(value=rev_map.get(cur_type, "MoYu"))
        ctk.CTkOptionMenu(sf, variable=type_var, values=list(type_map),
                          width=220,
                          command=lambda v: self._moyu_apply(en_var.get(), dev_var.get(), type_map[v])
                          ).pack(anchor="w", padx=14, pady=2)

        ctk.CTkLabel(sf, text="Wejście audio:", anchor="w").pack(anchor="w", padx=14, pady=(10, 0))
        names = [n for _, n in MoyuInput.list_devices()] or ["(brak wejść)"]
        saved = self.cfg.g("moyu", "device")
        dev_var = ctk.StringVar(value=saved if saved in names else names[0])
        ctk.CTkOptionMenu(sf, variable=dev_var, values=names, width=440,
                          command=lambda v: self._moyu_apply(en_var.get(), v, type_map[type_var.get()])
                          ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkSwitch(sf, text="Włącz timer audio", variable=en_var,
                      command=lambda: self._moyu_apply(en_var.get(), dev_var.get(), type_map[type_var.get()])
                      ).pack(anchor="w", padx=14, pady=12)
        self._moyu_status = ctk.CTkLabel(sf, text="", font=ctk.CTkFont(size=12), text_color="gray60")
        self._moyu_status.pack(anchor="w", padx=14)
        ctk.CTkLabel(sf, text="Podgląd na żywo (zrób solve, żeby sprawdzić):",
                     font=ctk.CTkFont(size=11), text_color="gray55").pack(anchor="w", padx=14, pady=(10, 0))
        self._moyu_live = ctk.CTkLabel(sf, text="—", font=ctk.CTkFont(size=30, weight="bold"))
        self._moyu_live.pack(anchor="w", padx=14)
        self._moyu_refresh()

    def _moyu_apply(self, enabled, device, mode=None):
        self.master._moyu_set_enabled(enabled, device, mode)
        self._moyu_refresh()

    def _moyu_refresh(self):
        if not getattr(self, "_moyu_status", None) or not self._moyu_status.winfo_exists():
            return
        m = self.master._moyu
        if m.running:
            self._moyu_status.configure(text=f"●  połączony: {m.device_name}", text_color="#5d5")
            self._moyu_live.configure(text=fmt(int(m.latest().get('time_milli', 0)) / 1000.0, 3))
        elif m.error:
            self._moyu_status.configure(text=f"błąd: {m.error}", text_color="#f66")
            self._moyu_live.configure(text="—")
        else:
            self._moyu_status.configure(text="wyłączony", text_color="gray60")
            self._moyu_live.configure(text="—")
        self.after(200, self._moyu_refresh)

    # ── shared helpers ────────────────────────────────────────────

    def _section(self, parent, row, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11),
                     text_color="gray50").grid(row=row, column=0, columnspan=4,
                     sticky="w", padx=14, pady=(12,0))

    def _color_row(self, parent, row, label, *path):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=row, column=0, sticky="w", padx=14, pady=6)
        cur = [self.cfg.g(*path)]
        sw  = ctk.CTkFrame(parent, width=30, height=26, corner_radius=6, fg_color=cur[0])
        sw.grid(row=row, column=1, padx=(0,6))
        sw.grid_propagate(False)
        def pick(s=sw):
            res = cc.askcolor(color=cur[0], parent=self)
            if res[1]:
                cur[0] = res[1]
                self.cfg.s(*path, res[1])
                s.configure(fg_color=res[1])
                self.on_change()
        ctk.CTkButton(parent, text="Wybierz", width=80, height=26,
                      command=pick).grid(row=row, column=2, padx=4)
        return sw

    def _switch_row(self, parent, row, label, *path):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=row, column=0, sticky="w", padx=14, pady=6)
        var = ctk.BooleanVar(value=self.cfg.g(*path))
        def tog(): self.cfg.s(*path, var.get()); self.on_change()
        ctk.CTkSwitch(parent, variable=var, text="", onvalue=True,
                      offvalue=False, command=tog).grid(
            row=row, column=1, columnspan=2, sticky="w", padx=8)
        return var

    # ── Wygląd ────────────────────────────────────────────────────

    def _tab_appearance(self, tab):
        sf = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sf.pack(fill="both", expand=True)
        sf.grid_columnconfigure(0, weight=1)
        self._color_swatches = {}

        self._section(sf, 0, "── Zoom UI ───────────────────────────")
        ctk.CTkLabel(sf, text="Skala interfejsu", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=1, column=0, sticky="w", padx=14, pady=6)
        zoom_pf = ctk.CTkFrame(sf, fg_color="transparent")
        zoom_pf.grid(row=1, column=1, columnspan=2, sticky="w", padx=8, pady=6)
        zv = ctk.DoubleVar(value=self.cfg.g("ui_zoom"))
        zlb = ctk.CTkLabel(zoom_pf, text=f"{zv.get():.0%}", width=44,
                           font=ctk.CTkFont(size=12))
        zlb.pack(side="right")
        def on_zoom(v):
            val = round(float(v) * 4) / 4  # snapping to 0.25 steps
            zv.set(val); zlb.configure(text=f"{val:.0%}")
            self.cfg.s("ui_zoom", val); self.on_change()
        ctk.CTkSlider(zoom_pf, from_=0.5, to=2.0, variable=zv,
                      command=on_zoom, width=180).pack(side="left")

        self._section(sf, 2, "── Scramble ─────────────────────────")
        ctk.CTkLabel(sf, text="Wyrównanie", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=3, column=0, sticky="w", padx=14, pady=6)
        alv = ctk.StringVar(value=self.cfg.g("scramble_align").capitalize())
        def on_align(v):
            self.cfg.s("scramble_align", v.lower()); self.on_change()
        ctk.CTkSegmentedButton(sf, values=["Left","Center","Right"],
                               variable=alv, command=on_align).grid(
            row=3, column=1, columnspan=2, sticky="w", padx=8, pady=6)

        self._section(sf, 4, "── Motyw ─────────────────────────────")
        ctk.CTkLabel(sf, text="Tryb kolorów", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=5, column=0, sticky="w", padx=14, pady=6)
        tv = ctk.StringVar(value=self.cfg.g("theme").capitalize())
        def on_theme(v):
            self.cfg.s("theme", v.lower())
            ctk.set_appearance_mode(v.lower()); self.on_change()
        ctk.CTkSegmentedButton(sf, values=["Dark","Light","System"],
                               variable=tv, command=on_theme).grid(
            row=5, column=1, columnspan=2, sticky="w", padx=8, pady=6)

        self._section(sf, 6, "── Gotowe palety kolorów ─────────────")
        ctk.CTkLabel(sf, text="Paleta", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=7, column=0, sticky="w", padx=14, pady=6)
        preset_var = ctk.StringVar(value=list(COLOR_PRESETS.keys())[0])
        pf = ctk.CTkFrame(sf, fg_color="transparent")
        pf.grid(row=7, column=1, columnspan=2, sticky="w", padx=8, pady=6)
        def apply_preset():
            name = preset_var.get()
            if name not in COLOR_PRESETS: return
            for key, val in COLOR_PRESETS[name].items():
                self.cfg.s("colors", key, val)
                if key in self._color_swatches:
                    self._color_swatches[key].configure(fg_color=val if val else "#555555")
            self.on_change()
        ctk.CTkOptionMenu(pf, variable=preset_var,
                          values=list(COLOR_PRESETS.keys()),
                          width=190).pack(side="left", padx=(0,8))
        ctk.CTkButton(pf, text="Zastosuj", width=80,
                      command=apply_preset).pack(side="left")

        self._section(sf, 8, "── Kolory timera (pojedynczo) ────────")
        color_keys = [
            ("Oczekiwanie",    "colors", "timer_idle"),
            ("Gotowość",       "colors", "timer_ready"),
            ("Biegnie",        "colors", "timer_running"),
            ("Inspekcja",      "colors", "timer_inspection"),
            ("DNF / kara",     "colors", "timer_penalty"),
            ("Tekst scrambla", "colors", "scramble"),
        ]
        for i, (lbl, *p) in enumerate(color_keys):
            sw = self._color_row(sf, 9+i, lbl, *p)
            self._color_swatches[p[-1]] = sw

        self._section(sf, 15, "── Tło aplikacji ─────────────────────")

        def _bg_color_row(parent, row, label, *path):
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=13),
                         anchor="w").grid(row=row, column=0, sticky="w", padx=14, pady=6)
            cur_val = [self.cfg.g(*path) or "#1a1a2e"]
            sw = ctk.CTkFrame(parent, width=30, height=26, corner_radius=6,
                              fg_color=cur_val[0])
            sw.grid(row=row, column=1, padx=(0,6)); sw.grid_propagate(False)
            self._color_swatches[path[-1]] = sw
            def pick(s=sw):
                res = cc.askcolor(color=cur_val[0], parent=self)
                if res[1]:
                    cur_val[0] = res[1]
                    self.cfg.s(*path, res[1]); s.configure(fg_color=res[1])
                    self.on_change()
            def clear():
                self.cfg.s(*path, ""); sw.configure(fg_color="#555555")
                self.on_change()
            bf = ctk.CTkFrame(parent, fg_color="transparent")
            bf.grid(row=row, column=2, padx=4)
            ctk.CTkButton(bf, text="Wybierz", width=72, height=26,
                          command=pick).pack(side="left", padx=(0,4))
            ctk.CTkButton(bf, text="Usuń", width=50, height=26,
                          fg_color="gray25", hover_color="gray35",
                          command=clear).pack(side="left")

        _bg_color_row(sf, 16, "Tło okna",   "colors", "bg_window")
        _bg_color_row(sf, 17, "Pasek górny","colors", "bg_header")

        self._section(sf, 18, "── Czcionki ──────────────────────────")

        ctk.CTkLabel(sf, text="Czcionka timera", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=19, column=0, sticky="w", padx=14, pady=6)
        tfv = ctk.StringVar(value=self.cfg.g("font", "timer_family"))
        def on_tf(v): self.cfg.s("font", "timer_family", v); self.on_change()
        ctk.CTkOptionMenu(sf, variable=tfv, values=FONT_FAMILIES,
                          command=on_tf, width=190).grid(
            row=19, column=1, columnspan=2, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(sf, text="Rozmiar timera", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=20, column=0, sticky="w", padx=14, pady=6)
        tsv = ctk.IntVar(value=self.cfg.g("font", "timer_size"))
        tvlb = ctk.CTkLabel(sf, text=str(tsv.get()), width=32)
        tvlb.grid(row=20, column=2, padx=4)
        def on_tsize(v):
            val = int(float(v)); tsv.set(val); tvlb.configure(text=str(val))
            self.cfg.s("font", "timer_size", val); self.on_change()
        ctk.CTkSlider(sf, from_=48, to=120, variable=tsv,
                      command=on_tsize, width=170).grid(row=20, column=1, padx=6)

        ctk.CTkLabel(sf, text="Czcionka scrambla", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=21, column=0, sticky="w", padx=14, pady=6)
        sfv = ctk.StringVar(value=self.cfg.g("font", "scramble_family"))
        def on_sf(v): self.cfg.s("font", "scramble_family", v); self.on_change()
        ctk.CTkOptionMenu(sf, variable=sfv, values=FONT_FAMILIES,
                          command=on_sf, width=190).grid(
            row=21, column=1, columnspan=2, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(sf, text="Rozmiar scrambla", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=22, column=0, sticky="w", padx=14, pady=6)
        ssv = ctk.IntVar(value=self.cfg.g("font", "scramble_size"))
        svlb = ctk.CTkLabel(sf, text=str(ssv.get()), width=32)
        svlb.grid(row=22, column=2, padx=4)
        def on_ssize(v):
            val = int(float(v)); ssv.set(val); svlb.configure(text=str(val))
            self.cfg.s("font", "scramble_size", val); self.on_change()
        ctk.CTkSlider(sf, from_=10, to=28, variable=ssv,
                      command=on_ssize, width=170).grid(row=22, column=1, padx=6)

    # ── Timer ─────────────────────────────────────────────────────

    def _tab_timer(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        self._section(tab, 0, "── Inspekcja ─────────────────────────")
        self._switch_row(tab, 1, "Włącz inspekcję przed startem",
                         "timer","inspection_enabled")

        ctk.CTkLabel(tab, text="Czas inspekcji", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=2, column=0, sticky="w", padx=14, pady=6)
        iv = ctk.StringVar(value=str(self.cfg.g("timer","inspection_duration"))+" s")
        def on_insp(v):
            self.cfg.s("timer","inspection_duration", int(v.replace(" s",""))); self.on_change()
        ctk.CTkOptionMenu(tab, variable=iv,
                          values=["10 s","12 s","15 s","20 s","25 s","30 s"],
                          command=on_insp, width=90).grid(row=2, column=1, sticky="w", padx=8)

        self._section(tab, 3, "── Sterowanie ────────────────────────")
        self._switch_row(tab, 4, "Ukryj czas podczas solva (blind mode)",
                         "timer","hide_during_solve")

        ctk.CTkLabel(tab, text="Opóźnienie startu", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=5, column=0, sticky="w", padx=14, pady=6)
        dv = ctk.StringVar(value=str(self.cfg.g("timer","start_delay_ms"))+" ms")
        def on_delay(v):
            self.cfg.s("timer","start_delay_ms", int(v.replace(" ms",""))); self.on_change()
        ctk.CTkOptionMenu(tab, variable=dv,
                          values=["0 ms","100 ms","200 ms","300 ms","500 ms"],
                          command=on_delay, width=100).grid(row=5, column=1, sticky="w", padx=8)

        self._section(tab, 6, "── Wyświetlanie ──────────────────────")
        ctk.CTkLabel(tab, text="Miejsca po przecinku", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=7, column=0, sticky="w", padx=14, pady=6)
        decv = ctk.StringVar(value=str(self.cfg.g("timer","decimals")))
        def on_dec(v): self.cfg.s("timer","decimals",int(v)); self.on_change()
        ctk.CTkSegmentedButton(tab, values=["1","2","3"], variable=decv,
                               command=on_dec).grid(row=7, column=1, sticky="w", padx=8)

        ctk.CTkLabel(tab, text="Odświeżanie timera", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=8, column=0, sticky="w", padx=14, pady=6)
        rfv = ctk.StringVar(value=str(self.cfg.g("timer","refresh_ms"))+" ms")
        def on_rf(v):
            self.cfg.s("timer","refresh_ms", int(v.replace(" ms",""))); self.on_change()
        ctk.CTkOptionMenu(tab, variable=rfv,
                          values=["16 ms","30 ms","50 ms","100 ms","200 ms"],
                          command=on_rf, width=100).grid(row=8, column=1, sticky="w", padx=8)

        self._section(tab, 10, "── Cel czasu / Sub-X ─────────────────")
        tgt_var = ctk.BooleanVar(value=self.cfg.g("target","enabled"))
        def on_tgt_en():
            self.cfg.s("target","enabled", tgt_var.get()); self.on_change()
        ctk.CTkSwitch(tab, text="Włącz cel czasu", variable=tgt_var,
                      command=on_tgt_en).grid(row=11, column=0, columnspan=2,
                      sticky="w", padx=14, pady=6)

        ctk.CTkLabel(tab, text="Cel (sekundy)", font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=12, column=0, sticky="w", padx=14, pady=6)
        tgt_entry = ctk.CTkEntry(tab, width=90, font=ctk.CTkFont(size=13),
                                  placeholder_text="np. 10.0")
        tgt_entry.insert(0, str(self.cfg.g("target","time")))
        tgt_entry.grid(row=12, column=1, sticky="w", padx=8)
        def save_tgt_time(e=None):
            try:
                v = float(tgt_entry.get().replace(",","."))
                self.cfg.s("target","time", v); self.on_change()
            except ValueError: pass
        tgt_entry.bind("<Return>", save_tgt_time)
        tgt_entry.bind("<FocusOut>", save_tgt_time)

        pb_var = ctk.BooleanVar(value=self.cfg.g("target","pb_sound"))
        def on_pb_snd():
            self.cfg.s("target","pb_sound", pb_var.get()); self.on_change()
        ctk.CTkSwitch(tab, text="Dźwięk przy PB", variable=pb_var,
                      command=on_pb_snd).grid(row=13, column=0, columnspan=2,
                      sticky="w", padx=14, pady=6)

    # ── Statystyki ────────────────────────────────────────────────

    def _tab_stats(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        self._section(tab, 0, "── Które statystyki pokazywać ────────")
        items = [
            ("Najlepszy czas",   "stats","show_best"),
            ("Ao5",              "stats","show_ao5"),
            ("Ao12",             "stats","show_ao12"),
            ("Ao100",            "stats","show_ao100"),
            ("Średnia sesji",    "stats","show_mean"),
        ]
        for i, (lbl, *p) in enumerate(items):
            self._switch_row(tab, i+1, lbl, *p)

        self._section(tab, len(items)+2, "── Własne średnie ───────────────────")

        add_row = ctk.CTkFrame(tab, fg_color="transparent")
        add_row.grid(row=len(items)+3, column=0, columnspan=3, sticky="w", padx=14, pady=4)
        entry_n = ctk.CTkEntry(add_row, placeholder_text="np. 2137", width=110,
                               font=ctk.CTkFont(size=12))
        entry_n.pack(side="left", padx=(0, 8))

        list_box = ctk.CTkFrame(tab, fg_color="transparent")
        list_box.grid(row=len(items)+4, column=0, columnspan=3, sticky="w", padx=14)

        def _refresh_custom():
            for w in list_box.winfo_children():
                w.destroy()
            for n in self.cfg.g("stats", "custom_averages"):
                rf = ctk.CTkFrame(list_box, fg_color="transparent")
                rf.pack(anchor="w", pady=1)
                ctk.CTkLabel(rf, text=f"Ao{n}", font=ctk.CTkFont(size=12),
                             width=70).pack(side="left")
                def _remove(x=n):
                    lst = self.cfg.g("stats", "custom_averages")
                    if x in lst:
                        lst.remove(x); self.cfg.s("stats", "custom_averages", lst)
                        self.on_change(); _refresh_custom()
                ctk.CTkButton(rf, text="✕", width=26, height=22,
                              fg_color="gray25", hover_color="#7a1010",
                              font=ctk.CTkFont(size=11),
                              command=_remove).pack(side="left", padx=(4, 0))

        def _add_custom():
            try:
                n = int(entry_n.get().strip())
                if n >= 2:
                    lst = self.cfg.g("stats", "custom_averages")
                    if n not in lst:
                        lst.append(n); lst.sort()
                        self.cfg.s("stats", "custom_averages", lst)
                        self.on_change(); _refresh_custom()
                entry_n.delete(0, "end")
            except ValueError:
                pass

        ctk.CTkButton(add_row, text="Dodaj", width=72,
                      command=_add_custom).pack(side="left")
        entry_n.bind("<Return>", lambda _: _add_custom())
        _refresh_custom()

    # ── Dane ──────────────────────────────────────────────────────

    def _tab_data(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        self._section_lbl(tab, "Bieżąca sesja")
        for text, cmd in [
            ("📤  Eksport sesji do CSV",    self._export_csv),
            ("✏️  Zmień nazwę sesji",        self._rename_session),
        ]:
            ctk.CTkButton(tab, text=text, anchor="w", width=300,
                          command=cmd).pack(anchor="w", padx=14, pady=3)
        ctk.CTkButton(tab, text="🗑  Usuń sesję", fg_color="#7a1010",
                      hover_color="#5a0a0a", anchor="w", width=300,
                      command=self._delete_session).pack(anchor="w", padx=14, pady=3)

        self._section_lbl(tab, "Import z innych aplikacji")
        ctk.CTkButton(tab, text="📥  Import z csTimer  (.json)",
                      anchor="w", width=300,
                      command=self._import_cstimer).pack(anchor="w", padx=14, pady=3)
        ctk.CTkButton(tab, text="📥  Import z Twisty Timer  (.csv)",
                      anchor="w", width=300,
                      command=self._import_twisty).pack(anchor="w", padx=14, pady=3)

        self._section_lbl(tab, "Backup / Przenoszenie na inne urządzenie")
        ctk.CTkButton(tab, text="📦  Eksportuj wszystko  (.rktimer)",
                      anchor="w", width=300,
                      command=self._export_backup).pack(anchor="w", padx=14, pady=3)
        ctk.CTkButton(tab, text="📥  Importuj backup  (.rktimer)",
                      anchor="w", width=300,
                      command=self._import_backup).pack(anchor="w", padx=14, pady=3)

        self._section_lbl(tab, "Usuń dane")
        ctk.CTkButton(tab, text="🗑  Usuń wszystkie czasy ze wszystkich sesji",
                      fg_color="#4a0808", hover_color="#380606",
                      anchor="w", width=300,
                      command=self._delete_all).pack(anchor="w", padx=14, pady=3)

    def _section_lbl(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=13, weight="bold"),
                     anchor="w").pack(anchor="w", padx=14, pady=(14,4))

    # ── backup ────────────────────────────────────────────────────

    def _export_backup(self):
        ts   = datetime.now().strftime("%Y%m%d_%H%M")
        path = fd.asksaveasfilename(
            defaultextension=".rktimer",
            filetypes=[("Rubik Timer Backup","*.rktimer"), ("ZIP","*.zip")],
            initialfile=f"rubik_backup_{ts}.rktimer",
            parent=self,
        )
        if not path: return
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for src, arc in [(DATA_FILE,"sessions.json"),(CFG_FILE,"settings.json")]:
                if os.path.exists(src):
                    zf.write(src, arc)
        mb.showinfo("Gotowe", f"Backup zapisany:\n{path}", parent=self)
        self.lift()

    def _import_backup(self):
        path = fd.askopenfilename(
            filetypes=[("Rubik Timer Backup","*.rktimer"), ("ZIP","*.zip")],
            parent=self,
        )
        if not path: return

        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = zf.namelist()
                has_sessions  = "sessions.json" in names
                has_settings  = "settings.json" in names

                answer = mb.askyesnocancel(
                    "Import",
                    "Jak chcesz zaimportować?\n\n"
                    "• TAK  → dołącz sesje do istniejących\n"
                    "• NIE  → zastąp wszystkie dane (czyste konto)\n"
                    "• ANULUJ → przerwij",
                    parent=self,
                )
                if answer is None: return

                if answer:  # merge
                    if has_sessions:
                        imp = json.loads(zf.read("sessions.json"))
                        for sname, sess in imp.get("sessions", {}).items():
                            if sname in self.sm._d["sessions"]:
                                self.sm._d["sessions"][sname]["times"].extend(
                                    sess.get("times", []))
                            else:
                                self.sm._d["sessions"][sname] = sess
                        self.sm._save()
                else:  # replace
                    if has_sessions:
                        zf.extract("sessions.json", DATA_DIR)
                        self.sm._d = self.sm._load()
                    if has_settings:
                        zf.extract("settings.json", DATA_DIR)

        except Exception as e:
            mb.showerror("Błąd importu", str(e), parent=self)
            return

        self.on_session_reload()
        mb.showinfo("Gotowe", "Import zakończony!", parent=self)
        self.lift()

    def _export_csv(self):
        cur   = self.sm.last
        times = self.sm.get(cur)["times"]
        path  = fd.asksaveasfilename(defaultextension=".csv",
                                     filetypes=[("CSV","*.csv")],
                                     initialfile=f"{cur}.csv", parent=self)
        if not path: return
        dec = self.cfg.g("timer","decimals")
        with open(path,"w",newline="",encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["#","Czas raw","Kara","Czas efektywny","Data","Scramble"])
            for i, e in enumerate(times,1):
                pen = e.get("penalty") or ""
                eff = effective(e)
                w.writerow([i, fmt(e["time"],dec), pen,
                             fmt(eff,dec) if eff!=float("inf") else pen,
                             e.get("date",""), e.get("scramble","")])
        self.lift()

    def _rename_session(self):
        cur = self.sm.last
        new = sd.askstring("Zmień nazwę", f"Nowa nazwa (obecna: {cur}):", parent=self)
        if not new or not new.strip() or new.strip()==cur: return
        self.sm.rename(cur, new.strip())
        self.on_session_reload()

    def _delete_session(self):
        cur = self.sm.last
        if len(self.sm.names) <= 1:
            mb.showwarning("Uwaga","Nie można usunąć ostatniej sesji.", parent=self); return
        if mb.askyesno("Usuń sesję", f"Usunąć sesję '{cur}'?", parent=self):
            self.sm.delete_session(cur)
            self.on_session_reload()

    def _delete_all(self):
        if mb.askyesno("Uwaga!","Usunąć WSZYSTKIE czasy ze wszystkich sesji?", parent=self):
            for name in self.sm.names:
                self.sm.get(name)["times"].clear()
            self.sm._save()
            self.on_session_reload()

    # ── import cstimer ────────────────────────────────────────────

    def _import_cstimer(self):
        path = fd.askopenfilename(
            filetypes=[("csTimer JSON","*.json"),("Wszystkie","*.*")], parent=self)
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            mb.showerror("Błąd", f"Nie można otworzyć pliku:\n{e}", parent=self); return

        added = 0
        cur = self.sm.last
        for key, val in data.items():
            if not key.startswith("session"): continue
            raw = val if isinstance(val, list) else val.get("d","") if isinstance(val, dict) else ""
            if isinstance(raw, str):
                solves = [s for s in raw.split("|") if s.strip()]
                for s in solves:
                    try:
                        parsed = json.loads(s)
                        pen_ms, t_ms = parsed[0][0], parsed[0][1]
                        scr = parsed[1] if len(parsed)>1 else ""
                        note = parsed[2] if len(parsed)>2 else ""
                        t = t_ms / 1000
                        penalty = None
                        if pen_ms == -2: penalty = "DNF"
                        elif pen_ms == 2000: penalty = "+2"
                        entry = {"time":t,"penalty":penalty,"scramble":scr,
                                 "note":note,"date":"","puzzle":"3x3"}
                        self.sm.get(cur)["times"].append(entry); added += 1
                    except Exception: pass
            elif isinstance(raw, list):
                for solve in raw:
                    try:
                        if not isinstance(solve, list) or len(solve)<1: continue
                        inner = solve[0]
                        if not isinstance(inner, list) or len(inner)<2: continue
                        pen   = inner[0]
                        t_ms  = inner[1]
                        scr   = solve[1] if len(solve)>1 else ""
                        note  = solve[2] if len(solve)>2 else ""
                        ts    = solve[3] if len(solve)>3 else 0
                        t = t_ms / 1000
                        penalty = None
                        if pen == -2: penalty = "DNF"
                        elif pen == 2000: penalty = "+2"
                        date_str = datetime.fromtimestamp(ts).isoformat() if ts else ""
                        entry = {"time":t,"penalty":penalty,"scramble":scr,
                                 "note":note,"date":date_str,"puzzle":"3x3"}
                        self.sm.get(cur)["times"].append(entry); added += 1
                    except Exception: pass
        if added:
            self.sm._save()
            self.on_session_reload()
        mb.showinfo("Import csTimer", f"Zaimportowano {added} solvów.", parent=self)
        self.lift()

    # ── import twisty timer ───────────────────────────────────────

    def _import_twisty(self):
        path = fd.askopenfilename(
            filetypes=[("Twisty Timer CSV","*.csv"),("Wszystkie","*.*")], parent=self)
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            mb.showerror("Błąd", f"Nie można otworzyć pliku:\n{e}", parent=self); return

        PUZZLE_MAP = {
            "3x3x3":"3x3","2x2x2":"2x2","4x4x4":"4x4","5x5x5":"5x5",
            "Pyraminx":"Pyraminx","Skewb":"Skewb","Megaminx":"Megaminx",
            "FTO":"FTO","Clock":"Clock",
        }
        added = 0; cur = self.sm.last
        for row in rows:
            try:
                t_ms  = int(row.get("Time(millis)","0"))
                pen   = int(row.get("Penalty","0"))
                scr   = row.get("Scramble","")
                note  = row.get("Comment","")
                date_ms = int(row.get("Date(millis)","0"))
                puzzle_raw = row.get("Puzzle","3x3x3")
                puzzle = PUZZLE_MAP.get(puzzle_raw, "3x3")
                t = t_ms / 1000
                penalty = None
                if pen == 2: penalty = "DNF"
                elif pen == 1: penalty = "+2"
                date_str = datetime.fromtimestamp(date_ms/1000).isoformat() if date_ms else ""
                entry = {"time":t,"penalty":penalty,"scramble":scr,
                         "note":note,"date":date_str,"puzzle":puzzle}
                self.sm.get(cur)["times"].append(entry); added += 1
            except Exception: pass
        if added:
            self.sm._save()
            self.on_session_reload()
        mb.showinfo("Import Twisty Timer", f"Zaimportowano {added} solvów.", parent=self)
        self.lift()

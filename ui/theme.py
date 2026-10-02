"""Colour palette and fonts shared by the main window and its panels.

Colours are (light, dark) tuples so customtkinter widgets follow the
appearance mode by themselves; plain tk widgets (Canvas) resolve them
through pick().
"""
import sys
import customtkinter as ctk


ACCENTS = {
    "Niebieski":    ("#3f63f2", "#6d8cff"),
    "Fiolet":       ("#7c4dff", "#a78bfa"),
    "Zielony":      ("#16a34a", "#4ade80"),
    "Turkus":       ("#0891b2", "#22d3ee"),
    "Pomarańcz":    ("#ea580c", "#fb923c"),
    "Róż":          ("#db2777", "#f472b6"),
    "Czerwony":     ("#dc2626", "#f87171"),
    "Złoty":        ("#b7791f", "#fbbf24"),
}

C = {
    "bg":           ("#eceff5", "#0d0f15"),
    "header":       ("#ffffff", "#12151d"),
    "panel":        ("#ffffff", "#161a24"),
    "panel_alt":    ("#f3f5fa", "#1c2130"),
    "row":          ("#ffffff", "#161a24"),
    "row_alt":      ("#f5f7fb", "#1a1f2b"),
    "border":       ("#d9dde7", "#262c3b"),
    "text":         ("#171a23", "#eceef5"),
    "muted":        ("#6a7184", "#8a91a5"),
    "faint":        ("#a3a9b8", "#555c70"),
    "button":       ("#e6e9f1", "#232938"),
    "button_hover": ("#d6dbe6", "#2e3548"),
    "good":         ("#15803d", "#4ade80"),
    "bad":          ("#dc2626", "#f87171"),
    "gold":         ("#b7791f", "#fbbf24"),
}


def accent(cfg):
    return ACCENTS.get(cfg.g("accent"), ACCENTS["Niebieski"])


def is_dark():
    return ctk.get_appearance_mode().lower() == "dark"


def pick(color):
    """Resolve a (light, dark) tuple (or a plain colour) for a raw tk widget."""
    if isinstance(color, (tuple, list)):
        return color[1] if is_dark() else color[0]
    return color


def mix(c1, c2, t):
    """Blend two #rrggbb colours: t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def tint(accent_pair, base_key, t):
    """(light, dark) colour: base surface tinted with t of the accent."""
    return (mix(C[base_key][0], accent_pair[0], t), mix(C[base_key][1], accent_pair[1], t))


_UI_FAMILY = None
_MONO_FAMILY = None


def _families():
    global _UI_FAMILY, _MONO_FAMILY
    if _UI_FAMILY is None:
        try:
            import tkinter.font as tkfont
            fams = set(tkfont.families())
        except Exception:
            fams = set()
        ui = ["Segoe UI Variable Display", "Segoe UI", "SF Pro Display",
              "Inter", "Helvetica Neue", "Cantarell", "DejaVu Sans"]
        mono = ["Cascadia Mono", "Consolas", "SF Mono", "Menlo",
                "JetBrains Mono", "DejaVu Sans Mono", "Courier New"]
        _UI_FAMILY = next((f for f in ui if f in fams),
                          "Segoe UI" if sys.platform == "win32" else "TkDefaultFont")
        _MONO_FAMILY = next((f for f in mono if f in fams), "Courier")
    return _UI_FAMILY, _MONO_FAMILY


def ui_family():
    return _families()[0]


def mono_family():
    return _families()[1]


def font(size=13, weight="normal", family=None):
    return ctk.CTkFont(family=family or ui_family(), size=size, weight=weight)


def _hover(acc):
    return [mix(acc[0], "#000000", 0.15), mix(acc[1], "#000000", 0.2)]


def install(cfg):
    """Point customtkinter's default theme at this palette + the chosen accent,
    so every window (settings, dialogs, tools) matches the main one.  Only
    affects widgets created afterwards."""
    acc = list(accent(cfg))
    L = lambda key: list(C[key])
    patch = {
        "CTk":                {"fg_color": L("bg")},
        "CTkToplevel":        {"fg_color": L("bg")},
        "CTkFrame":           {"fg_color": L("panel"), "top_fg_color": L("panel_alt"),
                               "border_color": L("border")},
        "CTkButton":          {"fg_color": acc, "hover_color": _hover(acc),
                               "text_color": ["#ffffff", "#ffffff"]},
        "CTkLabel":           {"text_color": L("text")},
        "CTkEntry":           {"fg_color": L("panel_alt"), "border_color": L("border"),
                               "text_color": L("text")},
        "CTkCheckBox":        {"fg_color": acc, "hover_color": _hover(acc),
                               "border_color": L("faint"), "text_color": L("text")},
        "CTkSwitch":          {"progress_color": acc, "fg_color": L("button_hover"),
                               "text_color": L("text")},
        "CTkSlider":          {"progress_color": acc, "button_color": acc,
                               "button_hover_color": _hover(acc), "fg_color": L("button_hover")},
        "CTkOptionMenu":      {"fg_color": L("button"), "button_color": L("button_hover"),
                               "button_hover_color": acc, "text_color": L("text")},
        "CTkSegmentedButton": {"fg_color": L("button"), "selected_color": acc,
                               "selected_hover_color": _hover(acc),
                               "unselected_color": L("button"),
                               "unselected_hover_color": L("button_hover"),
                               "text_color": [L("text")[0], "#ffffff"]},
        "CTkScrollbar":       {"button_color": L("button_hover"), "button_hover_color": L("faint")},
        "CTkScrollableFrame": {"label_fg_color": L("panel_alt")},
        "CTkTextbox":         {"fg_color": L("panel_alt"), "border_color": L("border"),
                               "text_color": L("text"),
                               "scrollbar_button_color": L("button_hover"),
                               "scrollbar_button_hover_color": L("faint")},
        "CTkComboBox":        {"fg_color": L("panel_alt"), "border_color": L("border"),
                               "button_color": L("button_hover"), "button_hover_color": acc},
        "CTkProgressBar":     {"progress_color": acc},
        "CTkRadioButton":     {"fg_color": acc, "hover_color": _hover(acc)},
        "DropdownMenu":       {"fg_color": L("panel"), "hover_color": L("button_hover"),
                               "text_color": L("text")},
    }
    t = ctk.ThemeManager.theme
    for widget, values in patch.items():
        if widget not in t:
            continue
        for k, v in values.items():
            if k in t[widget]:
                t[widget][k] = v

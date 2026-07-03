"""Small dialog for entering a time by hand (currently unused by the app's UI — manual entry is done via inline keyboard handling in App — kept as-is)."""
import customtkinter as ctk

from utils import _bring_to_front


class ManualTimeDialog(ctk.CTkToplevel):
    """Small dialog for entering a time by hand."""

    def __init__(self, parent, on_confirm):
        super().__init__(parent)
        self.title("Wpisz czas ręcznie")
        self.geometry("340x210")
        self.resizable(False, False)
        self.on_confirm = on_confirm

        ctk.CTkLabel(self, text="Wpisz czas lub karę:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(self,
                     text="Formaty: 12.345 · 1:23.456 · 12,345\nLub: DNF · DNS",
                     font=ctk.CTkFont(size=11), text_color="gray55").pack(pady=(0, 10))

        self.entry = ctk.CTkEntry(self, width=220, font=ctk.CTkFont(size=22),
                                  justify="center", placeholder_text="12.345")
        self.entry.pack(pady=(0, 14))
        self.entry.focus_set()

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()
        ctk.CTkButton(btn_row, text="Dodaj", width=100,
                      command=self._confirm).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Anuluj", width=100,
                      fg_color="gray30", hover_color="gray40",
                      command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda _: self._confirm())
        self.bind("<Escape>", lambda _: self.destroy())
        self.grab_set()
        _bring_to_front(self)

    def _confirm(self):
        raw = self.entry.get().strip()
        t, penalty = self._parse(raw)
        if t is None and penalty is None:
            self.entry.configure(border_color="#FF5555")
            return
        self.on_confirm(t or 0.0, penalty)
        self.destroy()

    @staticmethod
    def _parse(raw):
        up = raw.upper().replace(",", ".")
        if up in ("DNF", "DNS"):
            return 0.0, up
        try:
            if ":" in up:
                m, s = up.split(":", 1)
                return int(m) * 60 + float(s), None
            return float(up), None
        except ValueError:
            return None, None

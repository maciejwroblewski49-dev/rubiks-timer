# Faza 2, etap 1: podział `main.py` na moduły — design

## Cel

`main.py` (3915 linii) mieszkają razem: zapisywanie danych, symulacja 6
rodzajów kostek, generatory scrambli, dekoder sprzętowego timera (audio
StackMat/MoYu), 5 okien dialogowych i główna klasa `App` (state machine +
budowa UI). To utrudnia bezpieczne wprowadzanie zmian — im więcej rzeczy w
jednym pliku, tym łatwiej coś przypadkiem zepsuć gdzie indziej.

Ten etap to **czysty refaktor — zero zmiany zachowania**. Appka ma działać
identycznie po przeniesieniu kodu do osobnych plików. Żadnych poprawek
logiki, nowych funkcji ani zmian UI/UX przy okazji — to zostaje na etapy
2 (silnik statystyk) i 3 (wirtualizacja listy) tej samej Fazy 2.

## Mapa modułów

```
rubik-timer/
  main.py              # strażnik pojedynczej instancji (musi zostać PIERWSZY,
                        # przed ciężkimi importami) + `from app import App` +
                        # `App().mainloop()`
  utils.py              # fmt, display, effective, _bring_to_front — drobne,
                        # bezstanowe pomoce używane wszędzie
  scramble.py            # _gen, _OPP, gen_333...gen_mega, PUZZLES
  persistence.py          # DEFAULTS, Config, Sessions
  cube_sim.py             # _WCA_HEX, _MOVE_CYCLES(_2), _SKB_*, _C4_*,
                          # CubeState, Cube2State, Cube4State, SkewbState,
                          # FTOState, ClockState, _is_333_scramble,
                          # _make_viz_state, _viz_net_dims
  hardware_timer.py        # _AudioTimerDecoder, MoyuInput
  ui/
    __init__.py
    manual_time_dialog.py   # ManualTimeDialog
    time_detail_dialog.py   # TimeDetailDialog
    stat_detail_dialog.py   # StatDetailDialog
    settings_window.py      # SettingsWindow, COLOR_PRESETS, FONT_FAMILIES
    tools_window.py         # ToolsWindow (5 zakładek zostają razem w jednej
                            # klasie — to already-cohesive jeden widget, nie
                            # dzielę środka na osobne pliki)
  app.py                    # App (state machine + budowa głównego okna)
```

Każdy moduł ma jeden, jasny powód istnienia i może być rozumiany bez
czytania pozostałych. `ui/*` dostają instancję `App` jako parametr
konstruktora (`parent_app`) — nie importują klasy `App`, więc nie ma
cyklu importów mimo że `app.py` importuje z `ui/*`.

## Kolejność ekstrakcji

Moduły bez wewnętrznych zależności od pozostałych nowych plików idą
najpierw, żeby każdy krok dało się zweryfikować osobno bez czekania na
resztę:

1. `utils.py` → 2. `scramble.py` → 3. `persistence.py` →
   4. `hardware_timer.py` → 5. `cube_sim.py` → 6. `ui/*.py` (po kolei,
   każdy dialog osobno) → 7. `app.py` → 8. odchudzenie `main.py`

Po każdym kroku: wyciągnięcie kodu, poprawienie importów w miejscu
źródłowym i docelowym, `python -m py_compile` na wszystkich zmienionych
plikach, realne odpalenie aplikacji i ręczne sprawdzenie (patrz niżej),
commit. Jeśli coś się posypie — cofka o jeden krok, nie o cały refaktor.

## Weryfikacja

Brak automatycznych testów GUI w tym projekcie, więc po **każdym**
wyciągniętym module:

- `python -m py_compile` na zmienionych plikach
- realne uruchomienie `python main.py` (jak przy Fazie 1 i dodaniu 4x4) —
  sprawdzenie, że appka startuje bez wyjątków, okno jest responsywne,
  zamyka się czysto (plik blokady znika)
- ręczne przejście po funkcjach dotkniętych aktualnym krokiem (np. po
  wyciągnięciu `cube_sim.py`: sprawdzenie wizualizacji dla 3x3/Skewb/4x4;
  po `persistence.py`: solve zapisuje się i wczytuje poprawnie)
- dla `cube_sim.py` i `persistence.py` (czysta logika, łatwa do
  odizolowania) dorzucam lekkie testy pytest analogiczne do tych, które
  już powstały przy weryfikacji `Cube4State` — tanie ubezpieczenie na
  przyszłość, skoro i tak trzeba to ręcznie sprawdzić przy okazji

Dane produkcyjne (`C:\Users\User\Rubiks Timer\sessions.json`,
5293+ solve'ów) pozostają nietknięte przez cały proces — moduł
`persistence.py` po ekstrakcji musi czytać/pisać dokładnie te same
ścieżki (`DATA_DIR`/`DATA_FILE`/`CFG_FILE`) co dziś.

## Co jest poza zakresem tego etapu

- Żadnych zmian w logice statystyk (to etap 2)
- Żadnej wirtualizacji listy (to etap 3)
- Żadnych nowych funkcji ani zmian wyglądu
- Dalszy podział wewnątrz `ToolsWindow` (5 zakładek) — to jeden spójny
  widget, nie ma potrzeby dzielić go dalej na tym etapie

# Faza 2, etapy 2–3 + nowy wygląd i przesuwalne panele

## Co się zmieniło

**Silnik statystyk (`stats.py`, etap 2).** `SessionStats` trzyma efektywne czasy sesji
i aktualizuje statystyki przyrostowo: najlepszy/najgorszy, średnia, σ, aktualne aoN,
najlepsze aoN (z cache) oraz kroczące aoN dla każdego solva (dla kolumn listy i wykresu).
Po solvie liczy się tylko ostatnie okno zamiast całej sesji. Edycja kary albo usunięcie
czasu unieważnia tylko część okien od zmienionego miejsca.
Średnie obcinają domyślnie ceil(5%) czasów z każdej strony, tak jak WCA i csTimer
(ao5/ao12 → 1, ao50 → 3, ao100 → 5). Stary sposób („zawsze 1”) jest do wybrania
w Ustawienia → Statystyki.

**Wirtualna lista czasów (`ui/times_list.py`, etap 3).** Jeden `tk.Canvas`, który rysuje
tylko widoczne wiersze. Wcześniej każdy solve miał 3 widgety customtkinter. Lista ma
płynne przewijanie, kolumny ao5/ao12/ao50/ao100, wyróżnienie PB i kropkę przy notatce.

**Przesuwalne panele (`ui/layout.py`).** Okno główne to 5 paneli (scramble, timer,
statystyki, lista, podgląd kostki). Każdy ma względny prostokąt (0..1) zapisany
w `settings.json` → `layout.panels`. Klawisz **L** albo przycisk „✥ Układ” włącza tryb edycji:
belka panelu przesuwa go, róg ◢ zmienia rozmiar, krawędzie przyciągają się do okna,
środka i innych paneli. Do wyboru są gotowe układy. Każdy ma wariant z podglądem
kostki i bez niego, więc podgląd nie zasłania timera.

**Wygląd (`ui/theme.py`).** Jedna paleta (jasna/ciemna) i 8 kolorów akcentu.
`theme.install()` ustawia domyślny motyw customtkinter, więc okna ustawień i dialogi
pasują do okna głównego.

**Mniej zacinania.**
- `sessions.json` zapisuje się kompaktowo enkoderem C (z `indent=` json przechodził
  na wolny enkoder w Pythonie i blokował GIL) i atomowo (plik tymczasowy + rename).
- Okno Narzędzi odświeża tylko aktywną zakładkę, z opóźnieniem 250 ms.
- Szczegóły statystyki to jeden widget `tk.Text` zamiast ramki na każdy solve.

## Zmierzone (sesja 20 000 solvów, Xvfb)

| | czas |
|---|---|
| zapis solva (cały `_record`) | ~15 ms |
| przełączenie na sesję 20k | ~50 ms |
| okno „Najlepsze Ao12” | ~30 ms |

## Porządek

Jednorazowe skrypty `test_*.py` z katalogu głównego są teraz w `dev/cube_experiments/`
(pytest je wcześniej zbierał). `pytest.ini` ogranicza testy do `tests/`. Testy nie mają
już zaszytej ścieżki `C:\Users\...`.

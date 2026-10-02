# dev/

Narzędzia deweloperskie — **nie są częścią aplikacji** i nie są importowane przez `main.py`.

- `stackmat_test.py` — samodzielne okienko do diagnozy sygnału StackMat/MoYu z wejścia audio.
- `cube_experiments/` — jednorazowe skrypty z czasu pisania symulatora kostki
  (sprawdzanie cykli ruchów, orientacji, wizualizacji). Każdy jest samowystarczalny,
  uruchamia się go ręcznie: `py dev/cube_experiments/test_tperm.py`.

Prawdziwe testy automatyczne są w `tests/` (`py -m pytest`).

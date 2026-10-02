# tests/test_stats.py
import os
import random
import sys

MAIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MAIN_DIR)

from stats import SessionStats, average_last, rolling, trim_count, INF  # noqa: E402
from utils import effective  # noqa: E402


def _brute_ao(effs, n, mode):
    if len(effs) < n:
        return None
    w = sorted(effs[-n:])
    t = trim_count(n, mode)
    kept = w[t:len(w) - t] if t else w
    if any(v == INF for v in kept):
        return INF
    return sum(kept) / len(kept)


def _rand_entry(rng):
    r = rng.random()
    pen = "DNF" if r < 0.05 else ("+2" if r < 0.1 else None)
    return {"time": round(rng.uniform(8, 20), 3), "penalty": pen}


def test_trim_counts():
    assert trim_count(5) == 1
    assert trim_count(12) == 1
    assert trim_count(50) == 3
    assert trim_count(100) == 5
    assert trim_count(100, "one") == 1
    assert trim_count(2) == 0


def test_ao5_dnf_rules():
    effs = [10, 11, 12, 13, INF]
    assert average_last(effs, 5) == 12           # one DNF is trimmed
    assert average_last([10, 11, 12, INF, INF], 5) == INF


def test_rolling_matches_brute_force():
    rng = random.Random(1)
    effs = [effective(_rand_entry(rng)) for _ in range(300)]
    for n in (3, 5, 12, 50, 100):
        for mode in ("wca", "one"):
            got = rolling(effs, n, mode)
            exp = [_brute_ao(effs[:j + 1], n, mode) for j in range(n - 1, len(effs))]
            assert got == exp


def test_engine_incremental_ops_match_reload():
    rng = random.Random(7)
    times = [_rand_entry(rng) for _ in range(150)]
    eng = SessionStats("wca")
    eng.load(times)
    eng.rolling(5); eng.rolling(12)

    for step in range(200):
        op = rng.random()
        if op < 0.55 or not times:
            e = _rand_entry(rng); times.append(e); eng.append(e)
        elif op < 0.65:
            i = rng.randrange(len(times) + 1)
            e = _rand_entry(rng); times.insert(i, e); eng.insert(i, e)
        elif op < 0.8:
            i = rng.randrange(len(times))
            e = _rand_entry(rng); times[i] = e; eng.update(i, e)
        else:
            i = rng.randrange(len(times))
            times.pop(i); eng.delete(i)

        ref = SessionStats("wca"); ref.load(times)
        assert eng.count == ref.count
        assert eng.best == ref.best and eng.worst == ref.worst
        assert eng.valid_count == ref.valid_count
        if ref.mean is None:
            assert eng.mean is None
        else:
            assert abs(eng.mean - ref.mean) < 1e-9
        for n in (5, 12):
            assert eng.current(n) == ref.current(n)
            assert eng.rolling(n) == ref.rolling(n)
            assert eng.best_average(n) == ref.best_average(n)


def test_best_average_and_at():
    effs_times = [{"time": t, "penalty": None} for t in [12, 11, 10, 9, 8, 30, 30, 30]]
    eng = SessionStats("wca"); eng.load(effs_times)
    v, idx = eng.best_average(5)
    assert idx == 4 and v == 10
    assert eng.at(5, 4) == 10
    assert eng.at(5, 3) is None


def test_empty_session():
    eng = SessionStats()
    assert eng.best is None and eng.mean is None and eng.std is None
    assert eng.current(5) is None
    assert eng.best_average(5) == (None, None)
    assert eng.rolling(5) == []

"""Incremental statistics engine for a session: best/worst/mean, current aoN, best aoN, rolling averages.

Everything the main window shows after a solve is updated in (amortised)
O(N log N) for an aoN instead of re-scanning the whole session, so a
session with tens of thousands of solves stays as snappy as an empty one.
"""
import math
from bisect import bisect_left, insort

from utils import effective

INF = float("inf")

# How many results are dropped from EACH end of an aoN.
#   "wca" - csTimer/WCA convention: ceil(5% of N), at least 1 (ao5/ao12 -> 1,
#           ao50 -> 3, ao100 -> 5)
#   "one" - always exactly 1 (the old behaviour of this app)
TRIM_MODES = ("wca", "one")


def trim_count(n, mode="wca"):
    if n < 3:
        return 0
    if mode == "one":
        return 1
    return max(1, math.ceil(n * 0.05))


def _avg_sorted(window, t):
    """Trimmed mean of an already-sorted window. DNF if a DNF survives the trim."""
    kept = window[t:len(window) - t] if t else window
    if not kept:
        return None
    if kept[-1] == INF:
        return INF
    return sum(kept) / len(kept)


def average_last(effs, n, mode="wca"):
    """aoN of the last n effective times (None if there are fewer than n)."""
    if n < 1 or len(effs) < n:
        return None
    return _avg_sorted(sorted(effs[-n:]), trim_count(n, mode))


def rolling(effs, n, mode="wca", start=None):
    """aoN ending at every index >= start (default n-1), via a sliding sorted window."""
    out = []
    if n < 1 or len(effs) < n:
        return out
    t = trim_count(n, mode)
    s = n - 1 if start is None else max(n - 1, start)
    window = sorted(effs[s - n + 1:s + 1])
    out.append(_avg_sorted(window, t))
    for j in range(s + 1, len(effs)):
        del window[bisect_left(window, effs[j - n])]
        insort(window, effs[j])
        out.append(_avg_sorted(window, t))
    return out


class SessionStats:
    """Stats for one session, kept in sync with its list of time entries."""

    def __init__(self, mode="wca"):
        self.mode = mode
        self.load([])

    # ── sync with the session data ────────────────────────────────

    def load(self, times):
        self.effs = [effective(e) for e in times]
        self._rolling = {}          # n -> list, rolling[n][k] = aoN ending at k+n-1
        self._best_avg = {}         # n -> (value, end_index) cache
        self._recount()

    def set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            self._rolling.clear()
            self._best_avg.clear()

    def append(self, entry):
        v = effective(entry)
        self.effs.append(v)
        i = len(self.effs) - 1
        if v == INF:
            self.dnf_count += 1
        else:
            self._sum += v; self._sumsq += v * v; self.valid_count += 1
            if self.best is None or v < self.best:
                self.best, self.best_idx = v, i
            if self.worst is None or v > self.worst:
                self.worst, self.worst_idx = v, i
        for n, lst in self._rolling.items():
            if len(self.effs) >= n and len(lst) == len(self.effs) - n:
                v = average_last(self.effs, n, self.mode)
                lst.append(v)
                cached = self._best_avg.get(n)
                if cached is not None and v is not None and v != INF and \
                        (cached[0] is None or v < cached[0]):
                    self._best_avg[n] = (v, i)
            else:
                self._best_avg.pop(n, None)

    def update(self, i, entry):
        self.effs[i] = effective(entry)
        self._invalidate_from(i)
        self._recount()

    def delete(self, i):
        self.effs.pop(i)
        self._invalidate_from(i)
        self._recount()

    def _invalidate_from(self, i):
        # rolling[n][k] covers effs[k .. k+n-1]; anything touching index i or
        # later is stale (a delete also shifts everything after i).
        for n, lst in self._rolling.items():
            del lst[max(0, i - n + 1):]
        self._best_avg.clear()

    def _recount(self):
        valid = [v for v in self.effs if v != INF]
        self.valid_count = len(valid)
        self.dnf_count = len(self.effs) - len(valid)
        self._sum = sum(valid)
        self._sumsq = sum(v * v for v in valid)
        self.best = self.worst = None
        self.best_idx = self.worst_idx = None
        for i, v in enumerate(self.effs):
            if v == INF:
                continue
            if self.best is None or v < self.best:
                self.best, self.best_idx = v, i
            if self.worst is None or v > self.worst:
                self.worst, self.worst_idx = v, i

    # ── queries ───────────────────────────────────────────────────

    @property
    def count(self):
        return len(self.effs)

    @property
    def mean(self):
        return self._sum / self.valid_count if self.valid_count else None

    @property
    def std(self):
        if self.valid_count < 2:
            return None
        m = self.mean
        return math.sqrt(max(0.0, self._sumsq / self.valid_count - m * m))

    def median(self):
        valid = sorted(v for v in self.effs if v != INF)
        if not valid:
            return None
        k = len(valid)
        return valid[k // 2] if k % 2 else (valid[k // 2 - 1] + valid[k // 2]) / 2

    def current(self, n):
        return average_last(self.effs, n, self.mode)

    def rolling(self, n):
        """aoN ending at each solve, aligned to effs (None for the first n-1)."""
        if len(self.effs) < n:
            return [None] * len(self.effs)
        lst = self._rolling.setdefault(n, [])
        have = len(lst)
        need = len(self.effs) - n + 1
        if have < need:
            lst.extend(rolling(self.effs, n, self.mode, start=have + n - 1))
        return [None] * (n - 1) + lst

    def at(self, n, i):
        """aoN ending at solve i (None if i < n-1)."""
        if i < n - 1 or i >= len(self.effs):
            return None
        self.rolling(n)
        return self._rolling[n][i - n + 1]

    def best_average(self, n):
        """(value, end_index) of the best aoN in the session, or (None, None)."""
        if len(self.effs) < n:
            return None, None
        if n in self._best_avg and len(self._rolling.get(n, ())) == len(self.effs) - n + 1:
            return self._best_avg[n]
        self.rolling(n)
        lst = self._rolling[n]
        best_v, best_k = None, None
        for k, v in enumerate(lst):
            if v is not None and v != INF and (best_v is None or v < best_v):
                best_v, best_k = v, k
        res = (None, None) if best_v is None else (best_v, best_k + n - 1)
        self._best_avg[n] = res
        return res

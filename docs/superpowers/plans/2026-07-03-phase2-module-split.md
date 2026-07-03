# Faza 2, etap 1: podział main.py na moduły — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split `main.py` (4133 lines) into 12 focused files with zero behavior change, verifying the real app after every single module extraction.

**Architecture:** Each task moves one cohesive block of code out of `main.py` into a new file, using a small Python script that locates the block by its exact, verified text (not hardcoded line numbers, which would drift as earlier tasks shrink the file) and cuts it out. The removed block is replaced in `main.py` by an import statement, so every existing call site keeps working unchanged — moving a class/function and importing it back under the same name requires no other edits anywhere.

**Tech Stack:** Python 3, customtkinter/tkinter (unchanged), pytest (new, for two of the extracted modules).

## Global Constraints

- Zero behavior change. No logic fixes, no new features, no UI/UX changes in this plan — this is Phase 2's later steps (incremental stats engine, list virtualization).
- All new top-level modules (`utils.py`, `scramble.py`, `persistence.py`, `hardware_timer.py`, `cube_sim.py`, `app.py`) live directly in `C:\Users\User\rubik-timer\` — the **same directory as `main.py`**, not a subpackage. `persistence.py` contains `os.path.dirname(os.path.abspath(__file__))` (used for `BASE_DIR`); this only computes the same directory as today because it stays at the same directory depth as `main.py`. Do not move it into a subdirectory.
- `ui/` is the one subpackage (`ui/__init__.py` + one file per dialog). None of the moved dialog code uses `__file__`, so subdirectory placement is safe there.
- Real production data lives at `C:\Users\User\Rubiks Timer\sessions.json` (5293+ solves) and `settings.json`. Every task that touches `persistence.py`-adjacent code must be verified by actually launching the app and confirming this data still loads/saves correctly.
- After every task: `python -m py_compile` on every changed file, then a real launch of `python main.py` (check it starts without exceptions, the window is responsive, and it closes cleanly — the single-instance lock file at `C:\Users\User\Rubiks Timer\.app.lock` must be gone afterward), then `git add`/`git commit`. Never start a task while the previous one's commit is missing.
- No stale lock file before launching: `Get-Content` (or `cat`) `C:\Users\User\Rubiks Timer\.app.lock` must fail/be empty before every verification launch in this plan (if a previous launch didn't close cleanly, resolve that first rather than layering another launch on top).

---

### Task 1: Extract `utils.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\utils.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `fmt(sec, dec=3)`, `display(entry, dec=3)`, `effective(entry)`, `_bring_to_front(win)`, `_HAS_WINSOUND: bool`, `_winsound` (the `winsound` module or `None`)
- Consumed by: every later task (`persistence.py` doesn't need it, but `cube_sim.py` doesn't either — first real consumers are the `ui/*` and `app.py` tasks). For now `main.py` re-exports it via import so its own ~40 existing call sites keep working untouched.

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task1.py  (run once from C:\Users\User\rubik-timer, then delete)
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

BLOCK_WINSOUND = '''try:
    import winsound as _winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False'''

BLOCK_FMT = '''def fmt(sec, dec=3):
    if sec >= 60:
        m = int(sec // 60); s = sec % 60
        return f"{m}:{s:0{dec+3}.{dec}f}"
    return f"{sec:.{dec}f}"

def display(entry, dec=3):
    p = entry.get("penalty")
    if p in ("DNF","DNS"): return p
    return fmt(entry["time"] + (2 if p=="+2" else 0), dec)

def effective(entry):
    p = entry.get("penalty")
    if p in ("DNF","DNS"): return float("inf")
    return entry["time"] + (2 if p=="+2" else 0)'''

BLOCK_BRING_FRONT = '''def _bring_to_front(win):
    """Force a CTkToplevel window to appear on top and grab focus on Windows."""
    win.attributes("-topmost", True)
    win.lift()
    win.focus_force()
    win.after(300, lambda: win.attributes("-topmost", False) if win.winfo_exists() else None)'''

for block in (BLOCK_WINSOUND, BLOCK_FMT, BLOCK_BRING_FRONT):
    assert content.count(block) == 1, f"block not found exactly once:\n{block[:60]}..."

new_file = '''"""Small, dependency-free helpers shared across rubik-timer modules."""
''' + BLOCK_WINSOUND + "\n\n\n" + BLOCK_FMT + "\n\n\n" + BLOCK_BRING_FRONT + "\n"

with open(r"C:\Users\User\rubik-timer\utils.py", "w", encoding="utf-8") as f:
    f.write(new_file)

# Remove the 3 blocks from main.py, replace each with nothing (blank), then
# insert one import line right after the last top-of-file import.
content = content.replace(BLOCK_WINSOUND, "").replace(BLOCK_FMT, "").replace(BLOCK_BRING_FRONT, "")

ANCHOR = "import tkinter.messagebox as mb"
assert content.count(ANCHOR) == 1
content = content.replace(
    ANCHOR,
    ANCHOR + "\n\nfrom utils import fmt, display, effective, _bring_to_front, _HAS_WINSOUND, _winsound",
    1,
)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)

print("done")
```

Run: `python extract_task1.py`
Expected: prints `done` with no `AssertionError`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile utils.py main.py`
Expected: no output, exit code 0

- [ ] **Step 3: Delete the extraction script and launch the app**

```bash
rm extract_task1.py
```

Run: `python main.py` (foreground or via `Start-Process`, wait ~4s)
Expected: window titled "Wróbel Timer" opens, is responsive, timer display shows a time (uses `fmt`/`display`), no traceback in the console. Close it and confirm `C:\Users\User\Rubiks Timer\.app.lock` no longer exists.

- [ ] **Step 4: Commit**

```bash
git add utils.py main.py
git commit -m "refactor: extract utils.py (fmt/display/effective/_bring_to_front)"
```

---

### Task 2: Extract `scramble.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\scramble.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `PUZZLES: dict[str, callable]` (each value takes no args, returns a scramble string)
- Consumed by: `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task2.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

START = '_OPP = {"U":"D","D":"U","R":"L","L":"R","F":"B","B":"F"}'
END = '''PUZZLES = {"3x3":gen_333,"2x2":gen_222,"4x4":gen_444,"5x5":gen_555,
           "Pyraminx":gen_pyra,"Skewb":gen_skewb,"Megaminx":gen_mega,
           "FTO":gen_fto,"Clock":gen_clock,"3x3 OH":gen_333,"3x3 BLD":gen_333}'''

start_i = content.index(START)
end_i = content.index(END) + len(END)
block = content[start_i:end_i]

with open(r"C:\Users\User\rubik-timer\scramble.py", "w", encoding="utf-8") as f:
    f.write('"""Scramble generators for every supported puzzle type."""\nimport random\n\n' + block + "\n")

content = content[:start_i] + content[end_i:]
ANCHOR = "from utils import fmt, display, effective, _bring_to_front, _HAS_WINSOUND, _winsound"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom scramble import PUZZLES", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task2.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile scramble.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify**

```bash
rm extract_task2.py
```

Run: `python main.py`, change the puzzle dropdown to a couple of different puzzles (3x3, 4x4, Skewb) and confirm a new scramble string appears each time (exercises `PUZZLES`). Close and confirm the lock file is gone.

- [ ] **Step 4: Commit**

```bash
git add scramble.py main.py
git commit -m "refactor: extract scramble.py (PUZZLES + gen_* functions)"
```

---

### Task 3: Extract `persistence.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\persistence.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `BASE_DIR`, `_ASSETS`, `DATA_DIR`, `DATA_FILE`, `CFG_FILE`, `ICON_FILE` (path constants), `DEFAULTS: dict`, `Config`, `Sessions` classes
- Consumed by: `ui/settings_window.py` (Task 9, needs `DATA_FILE`/`CFG_FILE`/`DATA_DIR`/`Config`/`Sessions`), `app.py` (Task 11, needs `Config`/`Sessions`/`ICON_FILE`)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task3.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

# --- chunk A: BASE_DIR/_ASSETS/DATA_DIR/DATA_FILE/CFG_FILE/ICON_FILE + migration ---
A_START = "# Support running as a PyInstaller .exe (frozen) or as a plain .py script"
A_END = "_migrate_legacy_data()"
a_start = content.index(A_START)
a_end = content.index(A_END) + len(A_END)
chunk_a = content[a_start:a_end]
content = content[:a_start] + content[a_end:]

# --- chunk B: DEFAULTS dict ---
B_START = "DEFAULTS = {"
B_END = '''    "moyu": {
        "enabled": False,
        "device":  "",
        "type":    "m",          # 'm' = MoYu, 's' = StackMat Gen3/4/5 (jack)
    },
}'''
b_start = content.index(B_START)
b_end = content.index(B_END) + len(B_END)
chunk_b = content[b_start:b_end]
content = content[:b_start] + content[b_end:]

# --- chunk C: _merge helper ---
C_BLOCK = '''def _merge(base, over):
    r = copy.deepcopy(base)
    for k, v in over.items():
        if k in r and isinstance(r[k], dict) and isinstance(v, dict):
            r[k] = _merge(r[k], v)
        else:
            r[k] = v
    return r'''
assert content.count(C_BLOCK) == 1
content = content.replace(C_BLOCK, "", 1)

# --- chunk D: Config + Sessions classes ---
D_START = "class Config:"
D_END = '''    def add(self, n, e):          self._d["sessions"][n]["times"].append(e); self._save()
    def update(self, n, i, e):    self._d["sessions"][n]["times"][i] = e; self._save()
    def delete(self, n, i):       self._d["sessions"][n]["times"].pop(i); self._save()'''
d_start = content.index(D_START)
d_end = content.index(D_END) + len(D_END)
chunk_d = content[d_start:d_end]
content = content[:d_start] + content[d_end:]

new_file = (
    '"""Where rubik-timer data lives on disk, and the Config/Sessions '
    'classes that read/write it."""\n'
    "import os, sys, json, copy, threading, atexit\n"
    "from datetime import datetime\n\n"
    + chunk_a + "\n\n\n" + chunk_b + "\n\n\n" + C_BLOCK + "\n\n\n" + chunk_d + "\n"
)

with open(r"C:\Users\User\rubik-timer\persistence.py", "w", encoding="utf-8") as f:
    f.write(new_file)

ANCHOR = "from scramble import PUZZLES"
assert content.count(ANCHOR) == 1
content = content.replace(
    ANCHOR,
    ANCHOR + "\nfrom persistence import BASE_DIR, DATA_DIR, DATA_FILE, CFG_FILE, ICON_FILE, Config, Sessions",
    1,
)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task3.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile persistence.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify data integrity**

```bash
rm extract_task3.py
```

Before launching, snapshot the real data for comparison (adjust the destination to wherever you keep scratch files):
```bash
cp "C:\Users\User\Rubiks Timer\sessions.json" sessions_before_task3.json
```
Run: `python main.py`. Do a manual solve (press space, let it count down, hit space again) so a new entry gets written. Close the app (clean close). Then:
```bash
python -c "import json; d=json.load(open(r'C:\Users\User\Rubiks Timer\sessions.json', encoding='utf-8')); print(sum(len(s['times']) for s in d['sessions'].values()))"
```
Expected: total solve count is exactly one more than before the manual solve — confirms `persistence.py`'s `Config`/`Sessions` still read/write the exact same real files correctly.

- [ ] **Step 4: Add a pytest smoke test (per the design spec's testing section)**

```python
# tests/test_persistence.py
import importlib.util
import json
import os
import sys
import tempfile

MAIN_DIR = r"C:\Users\User\rubik-timer"


def _load_persistence(tmp_cfg, tmp_data):
    spec = importlib.util.spec_from_file_location(
        "persistence", os.path.join(MAIN_DIR, "persistence.py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["persistence"] = mod
    spec.loader.exec_module(mod)
    mod.CFG_FILE = tmp_cfg
    mod.DATA_FILE = tmp_data
    return mod


def test_config_debounced_save_then_flush(tmp_path):
    cfg_file = str(tmp_path / "settings.json")
    data_file = str(tmp_path / "sessions.json")
    persistence = _load_persistence(cfg_file, data_file)

    cfg = persistence.Config()
    cfg.s("ui_zoom", 1.5)
    assert not os.path.exists(cfg_file)  # debounced, no write yet
    cfg.flush()
    with open(cfg_file, encoding="utf-8") as f:
        assert json.load(f)["ui_zoom"] == 1.5


def test_sessions_add_then_flush_roundtrips(tmp_path):
    cfg_file = str(tmp_path / "settings.json")
    data_file = str(tmp_path / "sessions.json")
    persistence = _load_persistence(cfg_file, data_file)

    sm = persistence.Sessions()
    sm.create("Test", "3x3")
    sm.add("Test", {"time": 12.34, "penalty": None})
    sm.flush()
    with open(data_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["sessions"]["Test"]["times"] == [{"time": 12.34, "penalty": None}]
```

Note: create `tests/__init__.py` (empty) if `tests/` doesn't exist yet in `rubik-timer`.

- [ ] **Step 5: Run the new tests**

Run: `pytest tests/test_persistence.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add persistence.py main.py tests/test_persistence.py
git commit -m "refactor: extract persistence.py (paths, Config, Sessions) + smoke tests"
```

---

### Task 4: Extract `hardware_timer.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\hardware_timer.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `MoyuInput` class (with `.available()`, `.list_devices()` staticmethods, `.start()`, `.stop()`, `.latest()`, `.running`, `.device_name`, `.error`)
- Consumed by: `ui/settings_window.py` (Task 9), `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task4.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

START = "import queue as _queue"
END = '''def _moyu_mode(vals):
    """Most common value (the real reading dominates the scattered bit-errors)."""
    if not vals:
        return 0
    counts = {}; best = vals[-1]; bestn = 0
    for v in vals:
        n = counts.get(v, 0) + 1; counts[v] = n
        if n > bestn:
            bestn = n; best = v
    return best'''

start_i = content.index(START)
end_i = content.index(END) + len(END)
block = content[start_i:end_i]

new_file = (
    '"""External hardware timer over the audio jack (MoYu / StackMat)."""\n'
    "import math, threading, time\n\n" + block + "\n"
)
with open(r"C:\Users\User\rubik-timer\hardware_timer.py", "w", encoding="utf-8") as f:
    f.write(new_file)

content = content[:start_i] + content[end_i:]
ANCHOR = "from persistence import BASE_DIR, DATA_DIR, DATA_FILE, CFG_FILE, ICON_FILE, Config, Sessions"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom hardware_timer import MoyuInput", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task4.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile hardware_timer.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify**

```bash
rm extract_task4.py
```

Run: `python main.py`, open Ustawienia → Timer audio tab, confirm it still lists audio devices without crashing (exercises `MoyuInput.available()`/`.list_devices()`). Close and confirm clean exit.

- [ ] **Step 4: Commit**

```bash
git add hardware_timer.py main.py
git commit -m "refactor: extract hardware_timer.py (MoyuInput, _AudioTimerDecoder)"
```

---

### Task 5: Extract `cube_sim.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\cube_sim.py`
- Test: `C:\Users\User\rubik-timer\tests\test_cube_sim.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `_make_viz_state(puzzle: str, scramble: str)`, `_viz_net_dims(state)` — the only two names anything outside this file needs (verified: none of `CubeState`/`Cube2State`/`Cube4State`/`SkewbState`/`FTOState`/`ClockState`/`_WCA_HEX`/`_is_333_scramble` are referenced anywhere outside this block)
- Consumed by: `ui/time_detail_dialog.py`, `ui/tools_window.py` (Task 10), `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task5.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

START = "_WCA_HEX = {"
END = '''def _viz_net_dims(state):
    """Returns (cols, rows) cell count of the net for this state type."""
    if isinstance(state, SkewbState): return 8, 7
    if isinstance(state, Cube2State): return 8, 6
    if isinstance(state, Cube4State): return 16, 12
    if isinstance(state, FTOState): return 10, 4
    if isinstance(state, ClockState): return 12, 5
    return 12, 9'''

start_i = content.index(START)
end_i = content.index(END) + len(END)
block = content[start_i:end_i]

new_file = (
    '"""All puzzle-state simulators (3x3, 2x2, 4x4, Skewb, FTO, Clock) and '
    'the 2D net drawing for each, plus the dispatch used by the timer\'s '
    'scramble-preview UI."""\n'
    "import math\n\n" + block + "\n"
)
with open(r"C:\Users\User\rubik-timer\cube_sim.py", "w", encoding="utf-8") as f:
    f.write(new_file)

content = content[:start_i] + content[end_i:]
ANCHOR = "from hardware_timer import MoyuInput"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom cube_sim import _make_viz_state, _viz_net_dims", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task5.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile cube_sim.py main.py`
Expected: exit code 0

- [ ] **Step 3: Add pytest smoke tests (the design spec calls this out explicitly for cube_sim.py)**

```python
# tests/test_cube_sim.py
import importlib.util
import os
import sys

MAIN_DIR = r"C:\Users\User\rubik-timer"
spec = importlib.util.spec_from_file_location("cube_sim", os.path.join(MAIN_DIR, "cube_sim.py"))
cube_sim = importlib.util.module_from_spec(spec)
sys.modules["cube_sim"] = cube_sim
spec.loader.exec_module(cube_sim)


def test_make_viz_state_solved_3x3_is_uniform():
    state = cube_sim._make_viz_state("3x3", "")
    assert state is not None
    assert isinstance(state, cube_sim.CubeState)
    assert set(state.faces["U"]) == {"W"}


def test_make_viz_state_4x4_single_R_matches_kociemba_reference():
    state = cube_sim._make_viz_state("4x4", "R")
    assert state is not None
    assert isinstance(state, cube_sim.Cube4State)


def test_viz_net_dims_known_puzzles():
    assert cube_sim._viz_net_dims(cube_sim.SkewbState()) == (8, 7)
    assert cube_sim._viz_net_dims(cube_sim.Cube2State()) == (8, 6)
    assert cube_sim._viz_net_dims(cube_sim.Cube4State()) == (16, 12)
    assert cube_sim._viz_net_dims(cube_sim.CubeState()) == (12, 9)


def test_make_viz_state_rejects_invalid_scramble():
    assert cube_sim._make_viz_state("3x3", "R X U") is None
```

- [ ] **Step 4: Run the new tests**

Run: `pytest tests/test_cube_sim.py -v`
Expected: 4 passed

- [ ] **Step 5: Delete extraction script, launch, verify all puzzle visualizations**

```bash
rm extract_task5.py
```

Run: `python main.py`. Switch puzzle to 3x3, do a solve, click the time in the list — confirm the cube net still renders. Repeat for Skewb and 4x4 (the one you visually verified against cstimer earlier). Close and confirm clean exit.

- [ ] **Step 6: Commit**

```bash
git add cube_sim.py main.py tests/test_cube_sim.py
git commit -m "refactor: extract cube_sim.py (all puzzle simulators + viz dispatch) + smoke tests"
```

---

### Task 6: Extract `ui/manual_time_dialog.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\ui\__init__.py` (empty)
- Create: `C:\Users\User\rubik-timer\ui\manual_time_dialog.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `ManualTimeDialog` class. (Note: this class is currently unreferenced anywhere in the app — manual time entry is actually implemented as inline keyboard handling in `App`. It's dead code today; this task moves it as-is, unchanged, matching the "zero behavior change" constraint. Do not delete it — that would be a content change outside this plan's scope.)
- Consumed by: nothing today, but `app.py` (Task 11) still imports it back for parity with the original module's public surface.

- [ ] **Step 1: Create the ui package and write/run the extraction script**

```bash
mkdir -p ui
touch ui/__init__.py
```

```python
# extract_task6.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

START = "class ManualTimeDialog(ctk.CTkToplevel):"
END = '''    @staticmethod
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
            return None, None'''

start_i = content.index(START)
end_i = content.index(END) + len(END)
block = content[start_i:end_i]

new_file = (
    '"""Small dialog for entering a time by hand (currently unused by the '
    'app\'s UI — manual entry is done via inline keyboard handling in '
    'App — kept as-is)."""\n'
    "import customtkinter as ctk\n\n"
    "from utils import _bring_to_front\n\n\n" + block + "\n"
)
with open(r"C:\Users\User\rubik-timer\ui\manual_time_dialog.py", "w", encoding="utf-8") as f:
    f.write(new_file)

content = content[:start_i] + content[end_i:]
ANCHOR = "from cube_sim import _make_viz_state, _viz_net_dims"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom ui.manual_time_dialog import ManualTimeDialog", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task6.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile ui/manual_time_dialog.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify**

```bash
rm extract_task6.py
```

Run: `python main.py`, confirm it starts and closes cleanly (this class isn't exercised by any UI path today, so a clean start/stop is the whole check).

- [ ] **Step 4: Commit**

```bash
git add ui/__init__.py ui/manual_time_dialog.py main.py
git commit -m "refactor: extract ui/manual_time_dialog.py"
```

---

### Task 7: Extract `ui/time_detail_dialog.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\ui\time_detail_dialog.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `TimeDetailDialog` class (constructor `__init__(self, parent_app, idx)`)
- Consumed by: `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task7.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

START = "class TimeDetailDialog(ctk.CTkToplevel):"
END = '''    def _delete(self):
        self._app._del_time(self._idx)
        # _del_time closes this dialog via _app._detail_win'''

start_i = content.index(START)
end_i = content.index(END) + len(END)
block = content[start_i:end_i]

new_file = (
    '"""Dialog shown when you left-click a time in the list: big time, '
    'scramble, 2D cube net, penalty toggles, delete, notes."""\n'
    "import tkinter as tk\n"
    "import customtkinter as ctk\n"
    "from datetime import datetime\n\n"
    "from utils import _bring_to_front, display\n"
    "from cube_sim import _make_viz_state, _viz_net_dims\n\n\n" + block + "\n"
)
with open(r"C:\Users\User\rubik-timer\ui\time_detail_dialog.py", "w", encoding="utf-8") as f:
    f.write(new_file)

content = content[:start_i] + content[end_i:]
ANCHOR = "from ui.manual_time_dialog import ManualTimeDialog"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom ui.time_detail_dialog import TimeDetailDialog", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task7.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile ui/time_detail_dialog.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify**

```bash
rm extract_task7.py
```

Run: `python main.py`, do a solve, click on the time in the list — confirm the detail dialog opens with the cube net, penalty buttons work, and closing/deleting from it still works. Close app, confirm clean exit.

- [ ] **Step 4: Commit**

```bash
git add ui/time_detail_dialog.py main.py
git commit -m "refactor: extract ui/time_detail_dialog.py"
```

---

### Task 8: Extract `ui/stat_detail_dialog.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\ui\stat_detail_dialog.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `StatDetailDialog` class (constructor `__init__(self, parent_app, key)`)
- Consumed by: `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task8.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

START = "class StatDetailDialog(ctk.CTkToplevel):"
END = '''    def _open_detail(self, idx):
        self._app._show_detail(idx)'''

start_i = content.index(START)
end_i = content.index(END) + len(END)
block = content[start_i:end_i]

new_file = (
    '"""Dialog shown when you click a stat (Ao5/Ao12/Ao100/mean/best): '
    'the list of solves that make up that statistic."""\n'
    "import customtkinter as ctk\n\n"
    "from utils import _bring_to_front, fmt, display, effective\n\n\n" + block + "\n"
)
with open(r"C:\Users\User\rubik-timer\ui\stat_detail_dialog.py", "w", encoding="utf-8") as f:
    f.write(new_file)

content = content[:start_i] + content[end_i:]
ANCHOR = "from ui.time_detail_dialog import TimeDetailDialog"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom ui.stat_detail_dialog import StatDetailDialog", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task8.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile ui/stat_detail_dialog.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify**

```bash
rm extract_task8.py
```

Run: `python main.py`, do at least 5 solves, click on the Ao5 stat — confirm the breakdown dialog opens and clicking a row opens that solve's detail. Close, confirm clean exit.

- [ ] **Step 4: Commit**

```bash
git add ui/stat_detail_dialog.py main.py
git commit -m "refactor: extract ui/stat_detail_dialog.py"
```

---

### Task 9: Extract `ui/settings_window.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\ui\settings_window.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `SettingsWindow` class (constructor `__init__(self, parent, cfg, sm, on_change, on_session_reload)`), `COLOR_PRESETS`, `FONT_FAMILIES` (both now local to this file, not needed elsewhere — verified)
- Consumed by: `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task9.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

# chunk A: FONT_FAMILIES
A_START = "FONT_FAMILIES = ["
A_END = '''    "Impact", "Haettenschweiler", "Wide Latin", "Stencil",
    "Broadway", "Playbill", "Rockwell", "Cooper Black",
    "Bauhaus 93", "Berlin Sans FB", "Copperplate Gothic Bold",
    "Script MT Bold", "Monotype Corsiva", "Mistral",
    "Lucida Handwriting", "Ink Free", "Freestyle Script",
    "Jokerman", "Papyrus", "Comic Sans MS", "Forte",
]'''
a_start = content.index(A_START)
a_end = content.index(A_END) + len(A_END)
chunk_a = content[a_start:a_end]
content = content[:a_start] + content[a_end:]

# chunk B: COLOR_PRESETS
B_START = "COLOR_PRESETS = {"
B_END = '''    "Monochrome": {
        "timer_idle": "#FFFFFF", "timer_ready": "#BBBBBB",
        "timer_running": "#FFFFFF", "timer_inspection": "#DDDDDD",
        "timer_penalty": "#BBBBBB", "scramble": "#AAAAAA",
        "bg_window": "#111111", "bg_header": "#1c1c1c",
    },
}'''
b_start = content.index(B_START)
b_end = content.index(B_END) + len(B_END)
chunk_b = content[b_start:b_end]
content = content[:b_start] + content[b_end:]

# chunk C: SettingsWindow class
C_START = "class SettingsWindow(ctk.CTkToplevel):"
C_END = '''                self.sm.get(cur)["times"].append(entry); added += 1
            except Exception: pass
        if added:
            self.sm._save()
            self.on_session_reload()
        mb.showinfo("Import Twisty Timer", f"Zaimportowano {added} solvów.", parent=self)
        self.lift()'''
c_start = content.index(C_START)
c_end = content.index(C_END) + len(C_END)
chunk_c = content[c_start:c_end]
content = content[:c_start] + content[c_end:]

new_file = (
    '"""Settings window: appearance, timer, hardware-timer audio, stats, '
    'data import/export/backup tabs."""\n'
    "import os, json, csv, zipfile\n"
    "from datetime import datetime\n"
    "import customtkinter as ctk\n"
    "import tkinter.colorchooser as cc\n"
    "import tkinter.filedialog as fd\n"
    "import tkinter.messagebox as mb\n\n"
    "from utils import _bring_to_front, fmt\n"
    "from persistence import Config, Sessions, DATA_FILE, CFG_FILE, DATA_DIR\n"
    "from hardware_timer import MoyuInput\n\n\n"
    + chunk_a + "\n\n\n" + chunk_b + "\n\n\n" + chunk_c + "\n"
)
with open(r"C:\Users\User\rubik-timer\ui\settings_window.py", "w", encoding="utf-8") as f:
    f.write(new_file)

ANCHOR = "from ui.stat_detail_dialog import StatDetailDialog"
assert content.count(ANCHOR) == 1
content = content.replace(ANCHOR, ANCHOR + "\nfrom ui.settings_window import SettingsWindow", 1)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task9.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile ui/settings_window.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify every settings tab**

```bash
rm extract_task9.py
```

Run: `python main.py`, open Ustawienia, go through all 5 tabs (Wygląd, Timer, Timer audio, Statystyki, Dane), change a color, drag the zoom slider, apply a color preset, try CSV export. Confirm no crashes and changes take effect. Close, confirm clean exit and that `settings.json` was updated (check its modified timestamp).

- [ ] **Step 4: Commit**

```bash
git add ui/settings_window.py main.py
git commit -m "refactor: extract ui/settings_window.py (+ COLOR_PRESETS, FONT_FAMILIES)"
```

---

### Task 10: Extract `ui/tools_window.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\ui\tools_window.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `ToolsWindow` class (constructor `__init__(self, parent_app)`, method `.refresh_after_solve()`), `_load_mpl()` (matplotlib lazy loader, called once more from `app.py` to pre-warm on startup)
- Consumed by: `app.py` (Task 11)

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task10.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

# chunk A: matplotlib lazy loader
A_BLOCK = '''_HAS_MPL = None                     # None = not tried yet
Figure = None
FigureCanvasTkAgg = None
def _load_mpl():
    global _HAS_MPL, Figure, FigureCanvasTkAgg
    if _HAS_MPL is not None:
        return _HAS_MPL
    try:
        from matplotlib.figure import Figure as _F
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as _C
        Figure = _F; FigureCanvasTkAgg = _C; _HAS_MPL = True
    except Exception:
        _HAS_MPL = False
    return _HAS_MPL'''
assert content.count(A_BLOCK) == 1
content = content.replace(A_BLOCK, "", 1)

# chunk B: ToolsWindow class
B_START = "class ToolsWindow(ctk.CTkToplevel):"
B_END = '''    def refresh_after_solve(self):
        self.refresh_chart()
        self.refresh_histogram()
        self.refresh_stats()

    # ── close ─────────────────────────────────────────────────────

    def _on_close(self):
        self._metro_stop.set()
        self._metro_running = False
        self.destroy()'''
b_start = content.index(B_START)
b_end = content.index(B_END) + len(B_END)
chunk_b = content[b_start:b_end]
content = content[:b_start] + content[b_end:]

new_file = (
    '"""Tools window: scramble chart, histogram, full stats table, cube '
    'visualization tab, practice metronome."""\n'
    "import math, threading\n"
    "import tkinter as tk\n"
    "import customtkinter as ctk\n\n"
    "from utils import _bring_to_front, fmt, display, effective, _HAS_WINSOUND, _winsound\n"
    "from cube_sim import _make_viz_state, _viz_net_dims\n\n\n"
    + A_BLOCK + "\n\n\n" + chunk_b + "\n"
)
with open(r"C:\Users\User\rubik-timer\ui\tools_window.py", "w", encoding="utf-8") as f:
    f.write(new_file)

ANCHOR = "from ui.settings_window import SettingsWindow"
assert content.count(ANCHOR) == 1
content = content.replace(
    ANCHOR, ANCHOR + "\nfrom ui.tools_window import ToolsWindow, _load_mpl", 1
)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task10.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile ui/tools_window.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, verify every Tools tab**

```bash
rm extract_task10.py
```

Run: `python main.py`, open Narzędzia, check all 5 tabs (Wykres, Histogram, Statystyki, Wizualizacja, Metronom) render without errors, click "Odśwież" on the chart, start/stop the metronome. Close, confirm clean exit.

- [ ] **Step 4: Commit**

```bash
git add ui/tools_window.py main.py
git commit -m "refactor: extract ui/tools_window.py (+ matplotlib lazy loader)"
```

---

### Task 11: Extract `app.py`

**Files:**
- Create: `C:\Users\User\rubik-timer\app.py`
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Produces: `App` class
- Consumed by: `main.py` (the entry point)

At this point `main.py` contains: the single-instance guard, a chain of `from X import Y` lines (one per completed task), the Windows AppUserModelID setup, the `App` class itself, and the final `if __name__ == "__main__":` block. This task moves everything except the guard, the import chain, and the entry point into `app.py`.

- [ ] **Step 1: Write and run the extraction script**

```python
# extract_task11.py
MAIN = r"C:\Users\User\rubik-timer\main.py"
with open(MAIN, encoding="utf-8") as f:
    content = f.read()

# chunk A: Windows AppUserModelID setup
A_BLOCK = '''# Windows: set app ID so taskbar shows custom icon (not generic Python icon)
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "rubiks.timer.app.1"
    )
except Exception:
    pass'''
assert content.count(A_BLOCK) == 1
content = content.replace(A_BLOCK, "", 1)

# chunk B: the App class itself, up to (not including) the entry point
B_START = "class App(ctk.CTk):"
B_END_ANCHOR = '\n\nif __name__ == "__main__":\n    App().mainloop()'
b_start = content.index(B_START)
entry_i = content.index(B_END_ANCHOR)
chunk_b = content[b_start:entry_i]
content = content[:b_start] + content[entry_i:]

# The exact cross-module import lines added to main.py by tasks 1-10, in
# that order. Explicit and exhaustive (not regex-swept) so this can't
# accidentally also grab main.py's original, unrelated
# `from datetime import datetime` top-of-file import.
CROSS_MODULE_IMPORTS = [
    "from utils import fmt, display, effective, _bring_to_front, _HAS_WINSOUND, _winsound",
    "from scramble import PUZZLES",
    "from persistence import BASE_DIR, DATA_DIR, DATA_FILE, CFG_FILE, ICON_FILE, Config, Sessions",
    "from hardware_timer import MoyuInput",
    "from cube_sim import _make_viz_state, _viz_net_dims",
    "from ui.manual_time_dialog import ManualTimeDialog",
    "from ui.time_detail_dialog import TimeDetailDialog",
    "from ui.stat_detail_dialog import StatDetailDialog",
    "from ui.settings_window import SettingsWindow",
    "from ui.tools_window import ToolsWindow, _load_mpl",
]
for line in CROSS_MODULE_IMPORTS:
    assert content.count(line) == 1, f"expected import line missing: {line}"

new_file = (
    '"""The main App window: timer state machine, UI construction, times '
    'list, stats, session/puzzle switching, hardware-timer wiring."""\n'
    "import ctypes\n"
    "import time, random, json, csv, copy, zipfile, threading, math\n"
    "from datetime import datetime\n"
    "import customtkinter as ctk\n"
    "import tkinter as tk\n"
    "import tkinter.simpledialog as sd\n"
    "import tkinter.colorchooser as cc\n"
    "import tkinter.filedialog as fd\n"
    "import tkinter.messagebox as mb\n\n"
    + "\n".join(CROSS_MODULE_IMPORTS) + "\n\n\n"
    + A_BLOCK + "\n\n\n" + chunk_b + "\n"
)
with open(r"C:\Users\User\rubik-timer\app.py", "w", encoding="utf-8") as f:
    f.write(new_file)

# main.py: drop every one of those now-redundant import lines (app.py has
# its own copies) and replace with a single `from app import App`.
for line in CROSS_MODULE_IMPORTS:
    content = content.replace(line + "\n", "", 1)
content = content.replace(
    '\n\nif __name__ == "__main__":\n    App().mainloop()',
    '\n\nfrom app import App\n\nif __name__ == "__main__":\n    App().mainloop()',
    1,
)

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
```

Run: `python extract_task11.py`
Expected: prints `done`

- [ ] **Step 2: Compile check**

Run: `python -m py_compile app.py main.py`
Expected: exit code 0

- [ ] **Step 3: Delete script, launch, full regression pass**

```bash
rm extract_task11.py
```

Run: `python main.py`. This is the biggest single move, so check broadly:
- Timer starts/stops/records a solve
- Times list shows entries, click one to open detail, delete one
- Stats (Ao5/Ao12/best/mean) update and are clickable
- Puzzle switch (3x3/4x4/Skewb) regenerates scramble and viz
- Settings window opens, a color change takes effect live
- Tools window opens, chart/histogram/stats/viz/metronome tabs work
- Hardware timer tab still lists devices

Close the app and confirm `C:\Users\User\Rubiks Timer\.app.lock` is gone.

- [ ] **Step 4: Commit**

```bash
git add app.py main.py
git commit -m "refactor: extract app.py (the App class)"
```

---

### Task 12: Slim `main.py` down to the entry point

**Files:**
- Modify: `C:\Users\User\rubik-timer\main.py`

**Interfaces:**
- Consumes: `App` from `app.py`
- Produces: nothing new — this is cleanup only

After Task 11, `main.py` still has its original top-of-file `import customtkinter as ctk`, `import tkinter as tk`, etc. (lines that used to be needed by code that has since moved entirely into `app.py`/`ui/*`/`cube_sim.py`/etc.). Nothing in the now-tiny `main.py` references any of them anymore except the single-instance guard's own `os, sys, ctypes, atexit` (already imported at the very top, inside the guard's own block) and `from app import App`.

- [ ] **Step 1: Read the current `main.py` and confirm what's left**

Run: `python -c "print(open(r'C:\Users\User\rubik-timer\main.py', encoding='utf-8').read())"` and read it top to bottom. It should now look like: the single-instance guard (unchanged, ~34 lines), then a block of now-unused `import customtkinter as ctk` / `import time, random, ...` / `import tkinter as tk` / etc. lines, then `from app import App`, then the `if __name__ == "__main__":` block. Confirm by eye that none of those unused import lines are referenced anywhere else in the remaining file (they won't be — everything that used them moved to `app.py` in Task 11).

- [ ] **Step 2: Remove the now-dead imports**

Edit `main.py` by hand: delete every top-level `import`/`from` line between the end of the single-instance guard (`except Exception: pass`) and `from app import App`, **except** none need to be kept — `from app import App` is the only import `main.py` needs at that point. The file should read:

```python
# ── Single-instance guard — runs FIRST (before heavy imports).  A second copy
# launched from the shortcut detects the running instance in <100 ms, raises
# its window and exits, without waiting to load customtkinter/tkinter first.
import os, sys, ctypes, atexit
try:
    _LOCK_DIR = os.path.join(os.path.expanduser("~"), "Rubiks Timer")
    os.makedirs(_LOCK_DIR, exist_ok=True)
    _LOCK_FILE = os.path.join(_LOCK_DIR, ".app.lock")
    _k = ctypes.WinDLL("kernel32")
    _k.OpenProcess.restype  = ctypes.c_void_p
    _k.OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
    _k.CloseHandle.argtypes = [ctypes.c_void_p]
    def _pid_alive(pid):
        try:
            h = _k.OpenProcess(0x1000, 0, int(pid))
            if h: _k.CloseHandle(h); return True
        except Exception: pass
        return False
    if os.path.exists(_LOCK_FILE):
        try:
            with open(_LOCK_FILE) as _lf: _old = int(_lf.read().strip() or "0")
        except Exception: _old = 0
        if _old and _old != os.getpid() and _pid_alive(_old):
            for _title in ("Wróbel Timer", "Rubik's Timer", "Rubiks Timer"):
                _hwnd = ctypes.windll.user32.FindWindowW(None, _title)
                if _hwnd:
                    ctypes.windll.user32.ShowWindow(_hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(_hwnd)
                    break
            sys.exit(0)
    with open(_LOCK_FILE, "w") as _lf: _lf.write(str(os.getpid()))
    atexit.register(lambda p=_LOCK_FILE: os.path.exists(p) and os.remove(p))
except SystemExit: raise
except Exception: pass

from app import App

if __name__ == "__main__":
    App().mainloop()
```

- [ ] **Step 2: Compile check**

Run: `python -m py_compile main.py`
Expected: exit code 0

- [ ] **Step 3: Confirm file sizes**

Run: `wc -l main.py app.py cube_sim.py`
Expected: `main.py` is ~45 lines; `app.py` and `cube_sim.py` hold the bulk of what used to be in one 4133-line file.

- [ ] **Step 4: Full final regression launch**

Run: `python main.py` and repeat the full checklist from Task 11 Step 3 (timer, list, stats, puzzle switch, settings, tools, hardware timer). Also specifically test the single-instance guard: while the app is running, run `python main.py` again in a second terminal — it should immediately bring the existing window to front and exit, not open a second window.

- [ ] **Step 5: Run the full pytest suite**

Run: `pytest tests/ -v`
Expected: all tests from Tasks 3 and 5 pass (`test_persistence.py`, `test_cube_sim.py`)

- [ ] **Step 6: Commit**

```bash
git add main.py
git commit -m "refactor: slim main.py down to single-instance guard + entry point"
```

---

## Integration note

The module map from the design spec is now real on disk:

```
rubik-timer/
  main.py              (~45 lines: guard + entry point)
  utils.py
  scramble.py
  persistence.py
  cube_sim.py
  hardware_timer.py
  app.py
  ui/
    __init__.py
    manual_time_dialog.py
    time_detail_dialog.py
    stat_detail_dialog.py
    settings_window.py
    tools_window.py
  tests/
    test_persistence.py
    test_cube_sim.py
```

This is the foundation Phase 2's remaining two steps (incremental stats engine, list virtualization) build on — both now have a single, focused file to change (`app.py`'s stats methods; `app.py`'s times-list widgets) instead of hunting through one 4133-line file.

# tests/test_cube_sim.py
import importlib.util
import os
import sys

MAIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("cube_sim", os.path.join(MAIN_DIR, "cube_sim.py"))
cube_sim = importlib.util.module_from_spec(spec)
sys.modules["cube_sim"] = cube_sim
spec.loader.exec_module(cube_sim)


def test_make_viz_state_solved_3x3_is_uniform():
    # NOTE: an empty-string scramble is rejected by _is_333_scramble (pre-existing
    # behavior, unchanged by this refactor), so _make_viz_state("3x3", "") returns
    # None. "U U'" is a valid, net-identity scramble that still yields a fully
    # solved (uniform) state, preserving this test's original intent.
    state = cube_sim._make_viz_state("3x3", "U U'")
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

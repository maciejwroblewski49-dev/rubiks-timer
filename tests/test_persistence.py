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

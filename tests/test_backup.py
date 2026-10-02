# tests/test_backup.py
import os
import sys
import zipfile

MAIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MAIN_DIR)

import backup  # noqa: E402


def _setup(tmp_path, monkeypatch):
    data = tmp_path / "sessions.json"
    cfg = tmp_path / "settings.json"
    data.write_text('{"last": "a", "sessions": {}}', encoding="utf-8")
    cfg.write_text('{"theme": "dark"}', encoding="utf-8")
    monkeypatch.setattr(backup, "DATA_FILE", str(data))
    monkeypatch.setattr(backup, "CFG_FILE", str(cfg))
    monkeypatch.setattr(backup, "LOCAL_DIR", str(tmp_path / "backups"))


def test_backup_is_importable_rktimer(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    path = backup.make_backup(backup.LOCAL_DIR, keep=5)
    with zipfile.ZipFile(path) as zf:
        assert sorted(zf.namelist()) == ["sessions.json", "settings.json"]
    assert not any(n.endswith(".part") for n in os.listdir(backup.LOCAL_DIR))


def test_prune_keeps_newest(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    folder = backup.LOCAL_DIR
    os.makedirs(folder)
    for i in range(6):
        open(os.path.join(folder, f"rubiks_timer_2026-01-0{i + 1}_120000.rktimer"), "w").close()
    open(os.path.join(folder, "other_file.txt"), "w").close()
    backup.prune(folder, 3)
    left = sorted(os.listdir(folder))
    assert left == ["other_file.txt",
                    "rubiks_timer_2026-01-04_120000.rktimer",
                    "rubiks_timer_2026-01-05_120000.rktimer",
                    "rubiks_timer_2026-01-06_120000.rktimer"]


def test_due_and_cloud_copy(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert backup.due()
    cloud = tmp_path / "Drive" / backup.CLOUD_SUBDIR
    written = backup.write_all(14, str(cloud))
    assert len(written) == 2 and os.path.exists(written[1])
    assert not backup.due()


def test_missing_cloud_drive_does_not_fail(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("x")
    written = backup.write_all(14, str(blocker / "sub"))
    assert len(written) == 1

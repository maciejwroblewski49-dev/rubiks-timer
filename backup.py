"""Automatic backups of all solves + settings.

A backup is the same .rktimer zip as the manual "Eksportuj wszystko", so any
of them can be restored with "Importuj backup".  Copies go to a local folder
next to the data and, optionally, to a folder of a cloud drive (Google Drive /
OneDrive / Dropbox for desktop) - the drive's own app then uploads it.
"""
import os
import zipfile
from datetime import datetime

from persistence import DATA_DIR, DATA_FILE, CFG_FILE

LOCAL_DIR = os.path.join(DATA_DIR, "backups")
PREFIX = "rubiks_timer_"
EXT = ".rktimer"
CLOUD_SUBDIR = "Rubiks Timer - kopie"


def make_backup(folder, keep=14):
    """Zip sessions.json + settings.json into folder; keep the newest `keep`."""
    os.makedirs(folder, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = os.path.join(folder, f"{PREFIX}{stamp}{EXT}")
    part = path + ".part"
    with zipfile.ZipFile(part, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arc in ((DATA_FILE, "sessions.json"), (CFG_FILE, "settings.json")):
            if os.path.exists(src):
                zf.write(src, arc)
    os.replace(part, path)
    prune(folder, keep)
    return path


def list_backups(folder):
    """[(path, datetime)] newest first, only files this module wrote."""
    out = []
    try:
        names = os.listdir(folder)
    except OSError:
        return out
    for n in names:
        if n.startswith(PREFIX) and n.endswith(EXT):
            try:
                when = datetime.strptime(n[len(PREFIX):-len(EXT)], "%Y-%m-%d_%H%M%S")
            except ValueError:
                continue
            out.append((os.path.join(folder, n), when))
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def prune(folder, keep):
    for path, _ in list_backups(folder)[max(1, int(keep)):]:
        try:
            os.remove(path)
        except OSError:
            pass


def last_backup(folder):
    b = list_backups(folder)
    return b[0][1] if b else None


def cloud_candidates():
    """Cloud-drive folders that exist on this computer: [(label, folder)]."""
    home = os.path.expanduser("~")
    cands = []
    od = os.environ.get("OneDrive") or os.path.join(home, "OneDrive")
    cands.append(("OneDrive", od))
    cands.append(("Dropbox", os.path.join(home, "Dropbox")))
    cands.append(("iCloud", os.path.join(home, "iCloudDrive")))
    cands.append(("Google Drive", os.path.join(home, "Google Drive")))
    if os.name == "nt":
        # Google Drive for desktop mounts a drive letter (usually G:)
        for letter in "GHIJKLMNOPQRSTUVWXYZDEF":
            for sub in ("My Drive", "Mój dysk"):
                cands.append(("Google Drive", f"{letter}:{os.sep}{sub}"))
    seen, out = set(), []
    for label, base in cands:
        try:
            ok = os.path.isdir(base)
        except OSError:
            ok = False
        if ok and label not in seen:
            seen.add(label)
            out.append((label, os.path.join(base, CLOUD_SUBDIR)))
    return out


def due():
    """True when the newest local copy is missing or older than 20 h."""
    last = last_backup(LOCAL_DIR)
    return last is None or (datetime.now() - last).total_seconds() > 20 * 3600


def write_all(keep, cloud_dir=""):
    """Write a local copy and (if set) a cloud-folder copy. Files must be flushed first."""
    written = [make_backup(LOCAL_DIR, keep)]
    if cloud_dir:
        try:
            written.append(make_backup(cloud_dir, keep))
        except OSError:
            pass                  # drive not mounted right now - next time
    return written

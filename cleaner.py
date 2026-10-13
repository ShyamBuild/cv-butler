import os, time, subprocess, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE_DIR, "cleaner_state.json")
GRACE = 3600          # must be seen empty twice, >= 1h apart
JUNK = {'.DS_Store', 'Thumbs.db', '.localized'}

def _load():
    try:
        with open(STATE) as f: return json.load(f)
    except Exception:
        return {}

def _save(s):
    try:
        with open(STATE, "w") as f: json.dump(s, f, indent=2)
    except Exception: pass

def _trash(path):
    esc = path.replace('\\', '\\\\').replace('"', '\\"')
    try:
        r = subprocess.run(["osascript", "-e", f'tell application "Finder" to delete POSIX file "{esc}"'],
                           capture_output=True, timeout=30)
        return r.returncode == 0 and not os.path.exists(path)
    except Exception:
        return False

def _has_files(dirpath):
    for dp, dn, fn in os.walk(dirpath):
        for f in fn:
            if f not in JUNK: return True
    return False

ENABLED = False  # kill switch (set True to re-enable)

def clean_tree(root, say=print):
    if not ENABLED:
        return []
    root = os.path.abspath(root)
    state = _load()
    seen = state.get('seen', {})
    now = time.time()
    removed = []

    empty_now = set()
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if os.path.abspath(dirpath) == root: continue
        if os.path.basename(dirpath).startswith('.'): continue
        if _has_files(dirpath): continue
        empty_now.add(os.path.abspath(dirpath))

    for d in sorted(empty_now):
        if d in seen and now - seen[d] >= GRACE:
            if _trash(d):
                removed.append(os.path.relpath(d, root))
                seen.pop(d, None)
        else:
            seen[d] = now

    # forget entries that no longer exist or got files again
    seen = {k: v for k, v in seen.items() if os.path.isdir(k) and not _has_files(k)}
    _save({'seen': seen})

    if removed:
        say(f"\n🧹 [clean] {len(removed)} empty folder(s) moved to Trash (recoverable in Bin):")
        for r in removed: say(f"   🗑 {r}")
    return removed

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        clean_tree(sys.argv[1])

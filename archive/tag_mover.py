import os, re, sys, time, logging, logging.handlers, subprocess, plistlib, shutil, threading, zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VERSION = "tagtool v10 (act-immediately edition)"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(BASE_DIR, "tag_mover.lock")
LOG_FILE = os.path.join(BASE_DIR, "tag_mover.log")
DOC_EXTS = {'.pdf', '.doc', '.docx'}
COLOR_TAGS = {'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Gray', 'Grey'}
COOLDOWN = 10

_h = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
_h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log = logging.getLogger('tagtool')
log.setLevel(logging.INFO)
log.addHandler(_h)

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f: pid = int(f.read().strip())
            os.kill(pid, 0)
            print("⚠️ Another tagtool instance is already running. Close that Terminal window first.")
            sys.exit(1)
        except Exception:
            pass
    with open(LOCK_FILE, "w") as f: f.write(str(os.getpid()))

def _unescape(s):
    s = re.sub(r'\\U([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')

def _extract_from_plist(obj, out):
    if isinstance(obj, str):
        name = obj.split('\n')[0].strip()
        if name and name not in COLOR_TAGS:
            out.append(name)
    elif isinstance(obj, (list, tuple, set)):
        for item in obj:
            _extract_from_plist(item, out)

def _mdls_item(item, tags):
    item = item.rstrip(',')
    if not item: return
    if item.startswith('"') and item.endswith('"'):
        item = item[1:-1]
    name = _unescape(item).split('\n')[0].strip()
    if name and name not in COLOR_TAGS:
        tags.append(name)

def get_tags(path):
    if hasattr(os, 'getxattr'):
        try:
            data = os.getxattr(path, 'com.apple.metadata:_kMDItemUserTags')
            out = []
            _extract_from_plist(plistlib.loads(data), out)
            return out
        except Exception:
            pass
    try:
        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path],
                           capture_output=True, text=True, timeout=15)
        out = (r.stdout or '').strip()
        if not out or '(null)' in out: return []
        lines = out.splitlines()
        tags = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('kMDItemUserTags'):
                rest = line.split('=', 1)[1].strip() if '=' in line else ''
                if rest.startswith('(') and rest.endswith(')') and len(rest) > 1:
                    _mdls_item(rest[1:-1], tags)
                elif rest == '(':
                    i += 1
                    while i < len(lines):
                        item = lines[i].strip()
                        if item == ')': break
                        _mdls_item(item, tags)
                        i += 1
            i += 1
        return tags
    except Exception:
        return []

def sanitize_tag(name):
    return re.sub(r'[\\/:*?"<>|]', '', name).replace('\n', ' ').strip()

def doc_like(p):
    ext = os.path.splitext(p)[1].lower()
    if ext in DOC_EXTS: return True
    if ext == '':
        try:
            with open(p, 'rb') as f:
                head = f.read(4)
            if head == b'%PDF': return True
            if head == b'\xd0\xcf\x11\xe0': return True
            if head == b'PK\x03\x04':
                with zipfile.ZipFile(p) as z:
                    return 'word/document.xml' in z.namelist()
        except Exception:
            return False
    return False

def unique_dest(dest_dir, fn):
    cand = os.path.join(dest_dir, fn)
    if not os.path.exists(cand): return cand
    base, ext = os.path.splitext(fn)
    i = 1
    while True:
        cand = os.path.join(dest_dir, f"{base}_{i}{ext}")
        if not os.path.exists(cand): return cand
        i += 1

class TagMover:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        bn = os.path.basename(self.root).lower()
        self.root_is_position = bn.startswith('jd') or 'location' in bn
        self._processing = set()
        self._last = {}
        self.stats = {'checked': 0, 'tagged': 0, 'moved': 0, 'two': 0}
        self._lock = threading.Lock()

    def _dot(self):
        with self._lock:
            print(".", end="", flush=True)

    def _say(self, msg):
        with self._lock:
            print(msg, flush=True)

    def position_folder_for(self, path):
        """Deepest ancestor (up to root) that looks like a JD position folder."""
        cur = os.path.dirname(path)
        while True:
            bn = os.path.basename(cur).lower()
            if bn.startswith('jd') or 'location' in bn:
                return cur
            if cur == self.root: break
            parent = os.path.dirname(cur)
            if parent == cur: break
            cur = parent
        rel = os.path.relpath(os.path.dirname(path), self.root)
        if self.root_is_position or rel == '.':
            return self.root
        return os.path.join(self.root, rel.split(os.sep)[0])

    def consider(self, p, dot=False, force=False):
        try:
            p = os.path.abspath(p)
            if not os.path.isfile(p): return
            if not (p.startswith(self.root + os.sep) or os.path.dirname(p) == self.root): return
            if not doc_like(p): return
            now = time.time()
            if not force and now - self._last.get(p, 0) < COOLDOWN: return
            with self._lock:
                if p in self._processing: return
                self._processing.add(p)
                self._last[p] = now
        except Exception:
            return
        try:
            self._work(p, dot)
        finally:
            with self._lock:
                self._processing.discard(p)

    def _work(self, p, dot):
        try:
            if dot: self._dot()
            with self._lock:
                self.stats['checked'] += 1
            T = get_tags(p)
            if not T: return
            with self._lock:
                self.stats['tagged'] += 1
            if len(T) != 1:
                with self._lock:
                    self.stats['two'] += 1
                log.info(f"skip, 2+ tags {T}: {os.path.basename(p)}")
                return
            tag = sanitize_tag(T[0])
            if not tag: return
            P = self.position_folder_for(p)
            dest_dir = os.path.join(P, tag)
            if os.path.abspath(os.path.dirname(p)) == os.path.abspath(dest_dir): return
            os.makedirs(dest_dir, exist_ok=True)
            dest = unique_dest(dest_dir, os.path.basename(p))
            try:
                shutil.move(p, dest)   # safe on macOS even if the file is open
            except FileNotFoundError:
                log.info(f"file disappeared before move: {os.path.basename(p)}")
                return
            with self._lock:
                self.stats['moved'] += 1
            self._say(f"\n📦 {os.path.basename(p)} -> {os.path.relpath(dest, self.root)}")
            log.info(f"MOVED: {p} -> {dest}")
        except Exception as e:
            self._say(f"\n⚠️ MOVE FAILED: {os.path.basename(p)}: {e}")
            log.error(f"Move failed {p}: {e}")

    def scan(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for fn in filenames:
                if fn.startswith('.'): continue
                self.consider(os.path.join(dirpath, fn), dot=True)

def main():
    print(f"🏷️  {VERSION}")
    print("   your quiet tag-folder butler 🤖✨")
    if sys.platform != 'darwin':
        print("⚠️ tagtool uses macOS Finder tags — run it on a Mac.")
        sys.exit(1)
    acquire_lock()
    print("\nDRAG & DROP the folder that CONTAINS your tagged CVs, then press Return:")
    root = input("> ").strip().strip('"').strip("'").replace('\\', '')
    root = os.path.normpath(os.path.expanduser(root))
    if not os.path.isdir(root):
        print("Error: folder does not exist."); sys.exit(1)
    mover = TagMover(root)
    print("⏳ Scanning… (each dot = one file checked)")
    mover.scan()
    print()
    s = mover.stats
    print(f"✅ Scan complete: {s['checked']} files · {s['tagged']} tagged · {s['moved']} moved · {s['two']} with 2+ tags")
    print("👀 Watching silently… 1 tag = move · 2 tags = yours · tags never removed · nothing leaves its position folder")
    print("   moves happen even if the file is open (safe on macOS) · (Ctrl+C to quit)\n")
    from watchdog.observers import Observer as Obs
    class H(FileSystemEventHandler):
        def __init__(self): self.dirty = set(); self.lock = threading.Lock()
        def _add(self, p):
            with self.lock: self.dirty.add(p)
        def on_created(self, e):
            if not e.is_directory: self._add(e.src_path)
        def on_modified(self, e):
            if not e.is_directory: self._add(e.src_path)
        def on_moved(self, e):
            if not e.is_directory: self._add(e.dest_path)
    h = H()
    obs = Obs(); obs.schedule(h, path=root, recursive=True); obs.start()
    last_full = time.time(); last_hb = time.time(); n = 0
    try:
        while True:
            time.sleep(1)
            with h.lock:
                paths = list(h.dirty); h.dirty.clear()
            for p in paths: mover.consider(p, force=True)
            if time.time() - last_full > 15:
                last_full = time.time()
                mover.scan()
            if time.time() - last_hb > 120:
                last_hb = time.time(); n += 1
                print(f"💓 sweep #{n} · quiet · {mover.stats['moved']} moved total")
    except KeyboardInterrupt:
        obs.stop()
    finally:
        try: os.remove(LOCK_FILE)
        except Exception: pass
    obs.join()

if __name__ == "__main__":
    main()

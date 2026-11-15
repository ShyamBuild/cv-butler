import os, re, sys, time, logging, json, subprocess, shutil, zipfile, threading, urllib.request, urllib.parse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pdfplumber, openpyxl
try:
    import pypdfium2 as pdfium
except Exception:
    pdfium = None

VERSION = "v34 (Spotlight app-discovery converter edition)"
WATCH_FOLDER = ""
LLM_MODEL = None
OLLAMA_URL = "http://localhost:11434"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "processed.json")
LOCK_FILE = os.path.join(BASE_DIR, "cvtool.lock")
OCRBIN = os.path.join(BASE_DIR, "cvocr")
SWIFT_SRC = os.path.join(BASE_DIR, "cvocr.swift")
OCR_LOCK = threading.Lock()
OCR_SEM = threading.Semaphore(2)
LIBRE_PATHS = ("/Applications/LibreOffice.app/Contents/MacOS/soffice",
               "/System/Applications/LibreOffice.app/Contents/MacOS/soffice",
               os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"))
PAGES_PATHS = ("/Applications/Pages.app", "/System/Applications/Pages.app",
               os.path.expanduser("~/Applications/Pages.app"))
CHROME_PATHS = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"))
ENGINES = set()
LIBRE_BIN = None
BROWSER_BIN = None

SWIFT_CODE = '''
import Foundation
import Vision
import PDFKit
import AppKit

func ocr(_ page: PDFPage) -> String {
    let size = CGSize(width: 1500, height: 1950)
    let ns = page.thumbnail(of: size, for: .mediaBox)
    guard let cg = ns.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return "" }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["en-US"]
    req.usesLanguageCorrection = true
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do {
        try handler.perform([req])
        if let obs = req.results as? [VNRecognizedTextObservation] {
            return obs.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\\n")
        }
    } catch {}
    return ""
}

let args = CommandLine.arguments
guard args.count > 1, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else { exit(0) }
var pages: [String] = []
for i in 0..<min(doc.pageCount, 1) {
    if let p = doc.page(at: i) { pages.append(ocr(p)) }
}
print(pages.joined(separator: "\\n"))
'''

logging.basicConfig(filename='cv_organizer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_interruptible(futures):
    while True:
        _, not_done = wait(futures, timeout=1)
        if not not_done:
            return

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f: pid = int(f.read().strip())
            os.kill(pid, 0)
            print("⚠️ Another cvtool instance is already running. Close that Terminal window first.")
            sys.exit(1)
        except Exception:
            pass
    with open(LOCK_FILE, "w") as f: f.write(str(os.getpid()))

def _mdfind_app(bundle_id):
    """Find an app's .app path anywhere on disk via Spotlight."""
    try:
        r = subprocess.run(["mdfind", f"kMDItemCFBundleIdentifier == '{bundle_id}'"],
                           capture_output=True, text=True, timeout=15)
        for line in (r.stdout or "").splitlines():
            line = line.strip()
            if line and os.path.exists(line):
                return line
    except Exception:
        pass
    return None

def detect_engines():
    global LIBRE_BIN, BROWSER_BIN
    eng = []
    LIBRE_BIN = shutil.which("soffice") or next((p for p in LIBRE_PATHS if os.path.exists(p)), None) \
                or _mdfind_app('org.libreoffice.script')
    if LIBRE_BIN:
        if LIBRE_BIN.endswith('.app'):
            LIBRE_BIN = os.path.join(LIBRE_BIN, "Contents", "MacOS", "soffice")
        eng.append('libreoffice')
    BROWSER_BIN = next((p for p in CHROME_PATHS if os.path.exists(p)), None) \
                  or _mdfind_app('com.google.Chrome') or _mdfind_app('com.microsoft.edgemac') \
                  or _mdfind_app('com.brave.Browser') or _mdfind_app('com.operasoftware.Opera') \
                  or _mdfind_app('org.mozilla.firefox')
    if BROWSER_BIN:
        if BROWSER_BIN.endswith('.app'):
            BROWSER_BIN = os.path.join(BROWSER_BIN, "Contents", "MacOS", os.path.splitext(os.path.basename(BROWSER_BIN))[0])
        eng.append('html-pdf')
    if next((p for p in PAGES_PATHS if os.path.exists(p)), None) or _mdfind_app('com.apple.iWork.Pages'):
        eng.append('pages')
    if _mdfind_app('com.microsoft.Word'):
        eng.append('word')
    if 'pages' not in eng and 'word' not in eng:
        try:
            r = subprocess.run(["osascript", "-e", 'id of application "Pages"'], capture_output=True, timeout=15)
            if r.returncode == 0: eng.append('pages')
        except Exception:
            pass
    return eng

def ensure_ocr():
    if os.path.exists(OCRBIN): return True
    if not shutil.which("swiftc"):
        print("⚠️ swiftc not found — OCR disabled (other engines still active).")
        return False
    with OCR_LOCK:
        if os.path.exists(OCRBIN): return True
        try:
            with open(SWIFT_SRC, "w") as f: f.write(SWIFT_CODE)
            print("🛠 Building native OCR helper (one time, ~15s)…")
            r = subprocess.run(["swiftc", "-O", "-o", OCRBIN, SWIFT_SRC], capture_output=True, timeout=600)
            if r.returncode != 0:
                err = (r.stderr or b"").decode()[:600]
                print(f"⚠️ OCR build failed — OCR disabled. Compiler said: {err}")
                logging.error(f"OCR build failed: {err}")
                return False
            print("✅ OCR helper built successfully.")
            return os.path.exists(OCRBIN)
        except Exception as e:
            print(f"⚠️ OCR build error: {e} — OCR disabled.")
            logging.error(f"OCR build error: {e}")
            return False

def extract_text_ocr(file_path):
    if not os.path.exists(OCRBIN): return ""
    try:
        with OCR_SEM:
            r = subprocess.run([OCRBIN, file_path], capture_output=True, text=True, timeout=180)
        if not (r.stdout or "").strip():
            logging.info(f"OCR returned nothing for {os.path.basename(file_path)}")
        return r.stdout or ""
    except Exception as e:
        logging.error(f"OCR failed for {file_path}: {e}")
        return ""

def get_model():
    preferred = ['qwen2.5:3b-instruct', 'qwen2.5:3b', 'llama3.2', 'phi3', 'llama3', 'mistral', 'tinyllama']
    try:
        with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=10) as r:
            data = json.loads(r.read().decode())
        names = [m.get('name','') for m in data.get('models', []) if 'embed' not in m.get('name','').lower()]
        for p in preferred:
            for n in names:
                if n == p or n.split(':')[0] == p:
                    return n
        return names[0] if names else None
    except Exception as e:
        print(f"Could not contact Ollama: {e}")
        return None

def ask_ai(prompt):
    payload = json.dumps({
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert at parsing recruitment documents. Always respond with strict JSON only."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"num_ctx": 2048}
    }).encode()
    req = urllib.request.Request(OLLAMA_URL + "/api/chat", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.loads(r.read().decode())
    return res['message']['content']

def parse_ai_json(raw_content):
    if "```json" in raw_content: raw_content = raw_content.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_content: raw_content = raw_content.split("```")[1].split("```")[0].strip()
    return json.loads(raw_content)

def compact_text(text):
    text = re.sub(r'([A-Za-z])\1{3,}', r'\1', text)
    return re.sub(r'(?<=\b[A-Za-z]) (?=[A-Za-z]\b)', '', text)

HONORIFICS = {'mr', 'mrs', 'ms', 'dr', 'prof', 'er', 'late', 'capt', 'sir'}
LABELS = {'name', 'contact', 'email', 'mobile', 'phone', 'address', 'dob'}
PARTICLES = {'van', 'von', 'der', 'den', 'de', 'la', 'le', 'di', 'da', 'el', 'al', 'bin', 'binte', 'ter', 'ten'}

def polish_name(name):
    name = re.sub(r'\s+', ' ', name.strip())
    if ',' in name:
        a, b = [x.strip() for x in name.split(',', 1)]
        if a and b: name = f"{b} {a}"
    toks = name.split(' ')
    while toks and toks[0].lower().rstrip('.,:') in HONORIFICS:
        toks.pop(0)
    name = ' '.join(toks)
    toks = name.split(' ')
    out = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if len(t) == 1 and t.isalpha():
            run = t
            j = i + 1
            while j < len(toks) and len(toks[j]) == 1 and toks[j].isalpha():
                run += toks[j]; j += 1
            if j < len(toks) and len(run) <= 2:
                out.append(run + toks[j]); i = j + 1; continue
            if j >= len(toks) and out:
                out[-1] += run; i = j; continue
            out.append(run); i = j; continue
        out.append(t); i += 1
    return ' '.join(out)

def standard_name(name):
    n = sanitize_name(polish_name(name or '')).title()
    toks = n.split()
    for i in range(1, len(toks)):
        if toks[i].lower() in PARTICLES:
            toks[i] = toks[i].lower()
    return ' '.join(toks)

def sanitize_name(name):
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

def _as_escape(p):
    return p.replace('\\', '\\\\').replace('"', '\\"')

JOB_TITLES = {'graphic', 'designer', 'video', 'editor', 'motion', 'visual', 'animator', 'executive', 'manager', 'director', 'specialist', 'developer', 'engineer', 'analyst', 'consultant', 'intern', 'trainee', 'associate', 'seo', 'marketing', 'sales', 'hr', 'recruiter', 'content', 'writer', 'strategist', 'architect', 'planner', 'coordinator', 'officer', 'assistant', 'president', 'founder', 'co-founder', 'ceo', 'cto', 'cfo', 'cmo', 'marketer', 'general', 'management', 'operations', 'operation', 'top', 'plant', 'unit', 'factory', 'works', 'division', 'corporate', 'department', 'team', 'mobile', 'supply', 'chain', 'logistics', 'procurement', 'purchase', 'purchasing'}
TITLE_SUBSTR = {'marketer', 'designer', 'engineer', 'developer', 'manager', 'executive', 'specialist', 'analyst', 'consultant', 'director', 'recruiter', 'accountant', 'strategist', 'editor', 'animator', 'architect', 'coordinator', 'assistant', 'management', 'operations'}
BAD_WORDS = {'resume', 'curriculum', 'vitae', 'objective', 'career', 'summary', 'profile', 'cover', 'letter', 'application', 'portfolio', 'phone', 'email', 'contact', 'address', 'website', 'github', 'behance', 'dribbble', 'linkedin', 'location', 'pvt', 'ltd', 'llc', 'inc', 'corp', 'company', 'homes', 'pineapple', 'artstreet', 'sleepwell', 'kurlon', 'sheela', 'foam', 'sunsoft', 'technology', 'institute', 'university', 'college', 'school', 'board', 'senior', 'junior', 'strategy', 'driven', 'data', 'professional', 'permanent', 'present', 'notice', 'period', 'immediate', 'current', 'expected', 'lpa', 'ctc', 'years', 'experience', 'declaration', 'place', 'date', 'birth', 'gender', 'nationality', 'marital', 'status', 'languages', 'interests', 'father', 'mother', 'late', 'total', 'variable', 'digital', 'name', 'candidate', 'designation', 'position', 'dob', 'age', 'government', 'passionate', 'brief', 'highlights', 'qualification', 'qualifications', 'competencies', 'introduction', 'overview', 'snapshot', 'statement', 'skills', 'education', 'certifications', 'training', 'trainings', 'projects', 'achievements', 'expertise', 'hobbies', 'development', 'organization', 'growth', 'knowledge'}

def _junk(lt):
    if lt in JOB_TITLES or lt in BAD_WORDS: return True
    for p in re.split(r'[^a-z]+', lt):
        if p and (p in JOB_TITLES or p in BAD_WORDS): return True
    return False

def leading_name_run(line):
    out = []
    for t in line.split():
        core = t.rstrip('.,:')
        lt = core.lower()
        if not out and lt in HONORIFICS: continue
        if not out and lt in LABELS: continue
        if not core.isalpha(): break
        if _junk(lt): break
        out.append(core)
        if len(out) >= 4: break
    if any(len(t) == 1 for t in out): return []
    return out

def sane_name(name):
    toks = name.split()
    if not (1 <= len(toks) <= 4): return False
    for t in toks:
        if not re.fullmatch(r'[A-Za-z][A-Za-z.\-]+', t): return False
        trans = sum(1 for a, b in zip(t, t[1:]) if a.islower() != b.islower())
        if trans > 3: return False
    if len(re.findall(r'([A-Za-z])\1', name)) >= 3: return False
    return True

def valid_name(name, text, check_email=True):
    if not name or name == 'Unknown' or not (3 <= len(name) <= 40): return False
    toks = name.split()
    if any(t.lower() in BAD_WORDS for t in toks): return False
    if check_email:
        m = re.search(r'([\w.+-]+)@', text)
        if m:
            parts = set(re.split(r'[._\-+]', m.group(1).lower()))
            ntoks = [t.lower() for t in toks]
            if set(ntoks) <= parts: return False
    return True

def present_in_text(name, raw):
    low = raw.lower()
    for t in name.split():
        tt = t.lower().strip('.-')
        if len(tt) < 2: continue
        if tt not in low:
            return False
    return True

def has_personal_indicators(text):
    t = text.lower()
    return bool(re.search(r'[\w.+-]+@(gmail|yahoo|outlook|hotmail|icloud|rediffmail)\.', t)) or 'linkedin.com/in' in t or 'linkedin/in' in t

def ai_split_blob(blob):
    try:
        d = parse_ai_json(ask_ai(f"The string '{blob}' is a person's full name written without proper spacing (possibly lowercase). Insert the correct space(s) using ONLY the letters present — do NOT invent or add any extra words. Write it in Title Case (e.g. 'jatinchauhan' -> 'Jatin Chauhan'). Return ONLY valid JSON with key 'name'."))
        n = str(d.get('name', '')).strip()
        return n or None
    except Exception:
        return None

def ai_name_from_identifier(text):
    user = None
    m = re.search(r'behance\.net/([A-Za-z0-9\-]+)', text, re.I)
    if m: user = m.group(1)
    if not user:
        m = re.search(r'linkedin\.com/in/([A-Za-z0-9\-]+)', text, re.I)
        if m: user = m.group(1)
    if not user:
        m = re.search(r'([\w.+-]+)@(?:gmail|yahoo|outlook|hotmail|icloud|rediffmail)\.', text, re.I)
        if m: user = m.group(1)
    if not user: return None
    if '-' in user or '.' in user or '_' in user:
        parts = [p for p in re.split(r'[-._]', user) if p.isalpha() and len(p) >= 3]
        if len(parts) >= 2:
            return ' '.join(p.title() for p in parts[:2])
        return None
    letters = ''.join(c for c in user if c.isalpha())
    if len(letters) < 6: return None
    return ai_split_blob(letters)

def get_visual_name(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[0]
            words = page.extract_words(x_tolerance=3, y_tolerance=3, extra_attrs=["size"])
            if not words: return None
            page_height = page.height
            top_words = [w for w in words if float(w['top']) < page_height * 0.20]
            if not top_words: return None
            max_size = max(float(w['size']) for w in top_words)
            threshold = max_size * 0.85
            header_words = [w for w in top_words if float(w['size']) >= threshold]
            header_words.sort(key=lambda w: (float(w['top']), float(w['x0'])))
            lines = []
            current_line = []
            current_top = -1
            for w in header_words:
                if current_top == -1 or abs(float(w['top']) - current_top) < 5:
                    current_line.append(w)
                    current_top = float(w['top'])
                else:
                    lines.append(current_line)
                    current_line = [w]
                    current_top = float(w['top'])
            if current_line:
                lines.append(current_line)
            parsed = []
            for ws in lines:
                raw = " ".join(w['text'] for w in ws)
                clean = compact_text(raw)
                size = max(float(w['size']) for w in ws)
                parsed.append((clean, size, raw))
            for i, (clean, size, raw) in enumerate(parsed):
                run = leading_name_run(clean)
                if 2 <= len(run) <= 4 and sum(len(t) for t in run) >= 6:
                    if all(t[:1].isupper() for t in run) or clean.isupper():
                        return ' '.join(run)
                if len(run) == 1 and run[0].isalpha() and len(run[0]) >= 5 and (run[0].isupper() or run[0].istitle()):
                    if i + 1 < len(parsed):
                        nclean, nsize, nraw = parsed[i + 1]
                        nrun = leading_name_run(nclean)
                        if (len(nrun) == 1 and nrun[0].isalpha() and len(nrun[0]) >= 3
                                and ' ' not in raw and ' ' not in nraw and nsize >= size * 0.8):
                            return f"{run[0]} {nrun[0]}"
                    return run[0]
            return None
    except Exception as e:
        logging.error(f"Visual name extraction failed: {e}")
        return None

def heuristic_from_lines(lines):
    comp_lines = [compact_text(l.strip()) for l in lines if l.strip()]
    joined_lines = []
    i = 0
    while i < len(comp_lines):
        line = comp_lines[i]
        toks = line.split()
        if len(toks) == 1 and i + 1 < len(comp_lines):
            nxt = comp_lines[i + 1]
            nt = nxt.split()
            if (len(nt) == 1 and nt[0].isalpha() and toks[0].isalpha()
                    and (line.isupper() or line.istitle()) and (nxt.isupper() or nxt.istitle())):
                joined_lines.append(f"{line} {nxt}")
                i += 2
                continue
        joined_lines.append(line)
        i += 1
    for line in joined_lines[:8]:
        run = leading_name_run(line)
        if 2 <= len(run) <= 4 and sum(len(t) for t in run) >= 6:
            joined = ' '.join(run)
            if (joined.isupper() or joined.istitle()) and 2 <= len(joined) <= 40:
                return joined
        if len(run) == 1 and run[0].isalpha() and len(run[0]) >= 5 and (run[0].isupper() or run[0].istitle()):
            return run[0]
    return None

def filename_as_name(base_name):
    name = re.sub(r'[_\-]\d+$', '', base_name.strip())
    name = re.sub(r'\(\d+\)$', '', name)
    name = re.sub(r'\s*-\s*copy$', '', name, flags=re.I).strip()
    if not name: return None
    if not re.fullmatch(r'[A-Za-z][A-Za-z.\- ]+', name): return None
    if not (2 <= len(name) <= 40): return None
    toks = name.split()
    if not (1 <= len(toks) <= 4): return None
    if any(t.lower() in BAD_WORDS for t in toks): return None
    return name

def extract_text_pdfium(file_path):
    if pdfium is None: return ""
    try:
        doc = pdfium.PdfDocument(file_path)
        out = []
        for i, page in enumerate(doc):
            if i > 2: break
            out.append(page.get_textpage().get_text_bounded())
        return "\n".join(out)
    except Exception:
        return ""

def file_key(path):
    st = os.stat(path)
    return f"{st.st_ino}|{st.st_size}"

def load_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except Exception:
        return {}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f: json.dump(state, f, indent=2)
    except Exception:
        pass

def detect_type(path, ext):
    if ext in ('.pdf', '.doc', '.docx', '.xlsx'): return ext
    try:
        with open(path, 'rb') as f:
            head = f.read(8)
        if head.startswith(b'%PDF'): return '.pdf'
        if head.startswith(b'PK\x03\x04'):
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
            if 'word/document.xml' in names: return '.docx'
            if 'xl/workbook.xml' in names: return '.xlsx'
        if head[:4] == b'\xd0\xcf\x11\xe0': return '.doc'
    except Exception:
        pass
    return ext

def convert_with_libreoffice(doc_path, pdf_path):
    if not LIBRE_BIN or not os.path.exists(LIBRE_BIN): return False
    try:
        out_dir = os.path.dirname(pdf_path)
        subprocess.run([LIBRE_BIN, "--headless", "-env:UserInstallation=file:///tmp/cvtool_lo_profile",
                        "--convert-to", "pdf", "--outdir", out_dir, doc_path], capture_output=True, timeout=180)
        generated = os.path.join(out_dir, os.path.splitext(os.path.basename(doc_path))[0] + ".pdf")
        if os.path.exists(generated):
            if generated != pdf_path: os.replace(generated, pdf_path)
            return True
    except Exception:
        pass
    return False

def convert_with_html_pdf(doc_path, pdf_path):
    if not BROWSER_BIN or not os.path.exists(BROWSER_BIN): return False
    html_path = pdf_path + ".tmp.html"
    try:
        r = subprocess.run(["textutil", "-convert", "html", "-output", html_path, doc_path],
                           capture_output=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(html_path): return False
        url = "file://" + urllib.parse.quote(html_path)
        r2 = subprocess.run([BROWSER_BIN, "--headless", "--disable-gpu", "--no-sandbox",
                             "--user-data-dir=/tmp/cvtool_browser_profile",
                             "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", url],
                            capture_output=True, timeout=180)
        return r2.returncode == 0 and os.path.exists(pdf_path)
    except Exception:
        return False
    finally:
        try: os.remove(html_path)
        except Exception: pass

def convert_with_pages(doc_path, pdf_path):
    script = '''
    tell application "Pages"
        set theDoc to open POSIX file "%s"
        export theDoc to POSIX file "%s" as PDF
        close theDoc saving no
    end tell
    ''' % (_as_escape(doc_path), _as_escape(pdf_path))
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=90)
        return result.returncode == 0 and os.path.exists(pdf_path)
    except Exception:
        return False

def convert_with_word(doc_path, pdf_path):
    script = '''
    tell application "Microsoft Word"
        set theDoc to open file name "%s"
        save as theDoc file name "%s" file format format PDF
        close theDoc saving no
    end tell
    ''' % (_as_escape(doc_path), _as_escape(pdf_path))
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=180)
        return result.returncode == 0 and os.path.exists(pdf_path)
    except Exception:
        return False

class CVOrganizer(FileSystemEventHandler):
    def __init__(self, watch_folder):
        self.watch_folder = watch_folder
        self._seen = {}
        self._own = set()
        self._rc = {}
        self._ok_keys = set()
        self._noconv = set()
        self._jd_cache = {}
        self.state = load_state()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.conv_lock = threading.Lock()
        self._lock = threading.Lock()
        self.stats = {'renamed': 0, 'checked': 0}

    def _dot(self):
        with self._lock:
            print(".", end="", flush=True)

    def _say(self, msg):
        with self._lock:
            print(msg, flush=True)

    def _wait_stable(self, path, timeout=20):
        prev = -1
        stable = 0
        start = time.time()
        while time.time() - start < timeout:
            try:
                curr = os.path.getsize(path)
            except OSError:
                time.sleep(0.5); continue
            if curr == prev and curr > 0:
                stable += 1
                if stable >= 2: return True
            else:
                stable = 0
            prev = curr
            time.sleep(0.5)
        return True

    def on_created(self, event):
        if event.is_directory: return
        self._wait_stable(event.src_path)
        self.executor.submit(self.process_file, event.src_path)

    def on_modified(self, event):
        if event.is_directory: return
        self._wait_stable(event.src_path)
        self.executor.submit(self.process_file, event.src_path)

    def on_moved(self, event):
        if event.is_directory: return
        with self._lock:
            if event.dest_path in self._own:
                self._own.discard(event.dest_path)
                return
        try:
            with self._lock:
                self._ok_keys.discard(file_key(event.dest_path))
        except OSError:
            pass
        self._wait_stable(event.dest_path)
        self.executor.submit(self.process_file, event.dest_path)

    def process_file(self, file_path):
        try:
            p = os.path.abspath(file_path)
            now = time.time()
            with self._lock:
                if now - self._seen.get(p, 0) < 5: return
                self._seen[p] = now
            if not os.path.isfile(p): return
            try:
                key = file_key(p)
            except OSError:
                return
            with self._lock:
                if key in self._ok_keys: return
                self.stats['checked'] += 1
            self._dot()
            base, ext = os.path.splitext(os.path.basename(p))
            ftype = detect_type(p, ext.lower())
            if ftype in ('.doc', '.docx'):
                ok = self.handle_doc_conversion(p, key)
                if ok:
                    with self._lock: self._ok_keys.add(key)
            elif ftype == '.pdf':
                ok = self.handle_pdf(p, key)
                if ok:
                    with self._lock: self._ok_keys.add(key)
            elif ftype == '.xlsx':
                ok = self.handle_excel(p, key)
                if ok:
                    with self._lock: self._ok_keys.add(key)
            else:
                return
        except Exception as e:
            self._say(f"\n⚠️ ERROR processing {os.path.basename(file_path)}: {type(e).__name__}: {e}")
            logging.error(f"Critical error processing {file_path}: {e}")

    def handle_doc_conversion(self, file_path, key):
        with self.conv_lock:
            base = os.path.basename(file_path)
            pdf_path = os.path.splitext(file_path)[0] + ".pdf"
            entry = self.state.get(file_path)
            if isinstance(entry, dict) and entry.get('key') == key and entry.get('pdf'):
                if os.path.exists(entry['pdf']):
                    return True
            if os.path.exists(pdf_path):
                self._seen[pdf_path] = time.time()
                final = self.handle_pdf(pdf_path, key)
                self.state[file_path] = {'key': key, 'pdf': final or pdf_path}
                save_state(self.state)
                return True
            if file_path in self._noconv:
                return False
            okc = False
            if 'libreoffice' in ENGINES:
                okc = convert_with_libreoffice(file_path, pdf_path)
            if not okc and 'word' in ENGINES:
                okc = convert_with_word(file_path, pdf_path)
            if not okc and 'html-pdf' in ENGINES:
                okc = convert_with_html_pdf(file_path, pdf_path)
            if not okc and 'pages' in ENGINES:
                okc = convert_with_pages(file_path, pdf_path)
            if not okc:
                self._noconv.add(file_path)
                self._say(f"\n⚠️ No working converter for {base} (tried: {'/'.join(sorted(ENGINES)) or 'none'}). "
                          f"Install free 'Pages' from the App Store, then restart butler.")
                logging.error(f"No converter available for {file_path}")
                return False
            self._say(f"\n📄 converted: {base} -> {os.path.basename(pdf_path)}")
            logging.info(f"Converted: {file_path} -> {pdf_path}")
            self._seen[pdf_path] = time.time()
            time.sleep(0.5)
            final = self.handle_pdf(pdf_path, key)
            self.state[file_path] = {'key': key, 'pdf': final or pdf_path}
            save_state(self.state)
            return True

    def extract_text(self, file_path, file_type):
        text = ""
        if file_type == 'pdf':
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        if i > 2: break
                        page_text = page.extract_text()
                        if page_text: text += page_text + "\n"
            except Exception as e: logging.error(f"PDF read error: {e}")
        elif file_type == 'excel':
            try:
                wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                for ws in wb.worksheets:
                    text += f"[SHEET NAME: {ws.title}]\n"
                    for i, row in enumerate(ws.iter_rows(values_only=True)):
                        if i > 15: break
                        text += " ".join([str(cell) for cell in row if cell is not None]) + "\n"
                wb.close()
            except Exception as e: logging.error(f"Excel read error: {e}")
        return text

    def _ai_classify(self, text):
        prompt = f"Is the following text a Candidate CV/Resume, a Job Description (JD), or something else? Return ONLY valid JSON with key 'type' ('CV', 'JD', or 'Other'). Text: {text[:1500]}"
        try:
            data = parse_ai_json(ask_ai(prompt))
            return data.get('type', 'Other')
        except Exception:
            return 'Other'

    def _ai_extract_name(self, text):
        prompt = f"""The following text was OCR'd/extracted from a candidate's CV/resume.
Your task: Extract the candidate's PERSONAL FULL NAME exactly as displayed in the big header at the top (if the header shows a single name, return only that). If the header line starts with a label like 'Name:', ignore the label.
CRITICAL RULES:
1. The name is the big header at the top — prefer it over small contact-section text, LinkedIn URLs or emails.
2. DO NOT output the company name (e.g., 'Pineapple Homes', 'TCS', 'Sheela Foam').
3. DO NOT output the job title (e.g., 'Graphic Designer', 'Digital Marketer', 'General Manager') or title-words merged together.
4. DO NOT output the email address or parts of it, and never output labels like 'E-Mail', 'Name', 'Mobile'.
5. Fix any spacing artifacts (e.g., 'J A T I N' -> 'Jatin', 'M AYANK' -> 'Mayank', 'JATINCHAUHAN' -> 'Jatin Chauhan').
6. Remove honorifics (Mr., Mrs., Ms., Dr., Prof.) from the result.
Return ONLY valid JSON with key "name". If no personal name is found, return {{"name": "Unknown"}}.
Text: {text[:1500]}"""
        try:
            d = parse_ai_json(ask_ai(prompt))
            return str(d.get('name', ''))
        except Exception:
            return None

    def handle_pdf(self, file_path, key):
        try:
            return self._handle_pdf(file_path, key)
        except Exception as e:
            self._say(f"\n⚠️ ERROR on {os.path.basename(file_path)}: {type(e).__name__}: {e}")
            logging.error(f"handle_pdf crash on {file_path}: {e}")
            return None

    def _handle_pdf(self, file_path, key):
        base = os.path.basename(file_path)
        base_no_ext = os.path.splitext(base)[0]

        if self._rc.get(key, 0) >= 3:
            return file_path

        text = self.extract_text(file_path, 'pdf')
        if not text.strip():
            text = extract_text_pdfium(file_path)

        ocr = ""
        ocr_attempted = False
        if not text.strip():
            ocr_attempted = True
            ocr = extract_text_ocr(file_path)
            if ocr.strip():
                logging.info(f"{base}: empty text layer -> OCR used")
            text = ocr

        if not text.strip():
            fixed = standard_name(base_no_ext)
            if len(fixed.split()) == 1 and len(fixed) >= 6:
                split = ai_split_blob(fixed)
                if split and sane_name(split): fixed = split
            if (not base.lower().startswith('jd') and len(fixed.split()) >= 2
                    and sane_name(fixed) and valid_name(fixed, "", False) and f"{fixed}.pdf" != base):
                r = self.rename_file_safely(file_path, f"{fixed}.pdf", key, tag='casefix')
                return r or file_path
            return file_path

        ai_text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text)
        indicators = has_personal_indicators(ai_text)

        if base.lower().startswith('jd'):
            return file_path
        cv_keywords = ['experience', 'education', 'skills', 'profile', 'summary', 'objective', 'projects', 'achievements', 'internship', 'certifications', 'employment', 'qualifications', 'expertise']
        jd_keywords = ['job description', 'responsibilities', 'requirements', 'desired candidate', 'about the company', 'per annum', 'ctc', 'walk-in', 'hiring for', 'candidate should have']
        t_lower = ai_text.lower()
        cv_score = sum(1 for k in cv_keywords if k in t_lower)
        jd_score = sum(1 for k in jd_keywords if k in t_lower)

        is_cv = False
        if cv_score >= 2 and cv_score > jd_score:
            is_cv = True
        elif jd_score >= 2 and jd_score > cv_score:
            return file_path
        else:
            res = self._ai_classify(ai_text)
            if res == 'JD': return file_path
            if res == 'CV': is_cv = True
        if not is_cv:
            return file_path

        cur_std = standard_name(base_no_ext)
        cur_toks = set(t.lower() for t in cur_std.split())

        v_name = get_visual_name(file_path)
        if v_name:
            v_name = standard_name(v_name)
            if not (sane_name(v_name) and valid_name(v_name, ai_text, False)): v_name = None

        if not ocr_attempted and v_name is None:
            ocr = extract_text_ocr(file_path)
        combined = (ocr + "\n" + ai_text) if ocr.strip() else ai_text

        h_ocr = heuristic_from_lines(ocr.split('\n')) if ocr.strip() else None
        if h_ocr:
            h_ocr = standard_name(h_ocr)
            if not (sane_name(h_ocr) and valid_name(h_ocr, combined, False)): h_ocr = None
        h_txt = heuristic_from_lines(text.split('\n'))
        if h_txt:
            h_txt = standard_name(h_txt)
            if not (sane_name(h_txt) and valid_name(h_txt, combined, False)): h_txt = None

        if v_name:
            if f"{v_name}.pdf" != base:
                r = self.rename_file_safely(file_path, f"{v_name}.pdf", key, tag='visual')
                return r or file_path
            return file_path

        det = [n for n in (h_ocr, h_txt) if n]
        if det:
            c = Counter(det)
            best, cnt = c.most_common(1)[0]
            if cnt == 1:
                best = next(n for n in (h_ocr, h_txt) if n)
            best_toks = set(t.lower() for t in best.split())
            if len(cur_toks) >= 2 and best_toks < cur_toks:
                return file_path
            if f"{best}.pdf" != base:
                r = self.rename_file_safely(file_path, f"{best}.pdf", key, tag='ocr/text')
                return r or file_path
            return file_path

        a_name = self._ai_extract_name(combined)
        ai_ok = None
        if a_name and a_name != 'Unknown':
            a_name = standard_name(a_name)
            if len(a_name.split()) >= 1 and sane_name(a_name) and valid_name(a_name, combined, True) and present_in_text(a_name, combined):
                ai_ok = a_name
        if ai_ok:
            if f"{ai_ok}.pdf" != base:
                r = self.rename_file_safely(file_path, f"{ai_ok}.pdf", key, tag='ai')
                return r or file_path
            return file_path

        id_name = ai_name_from_identifier(combined)
        if id_name:
            id_name = standard_name(id_name)
            if len(id_name.split()) >= 2 and sane_name(id_name) and valid_name(id_name, combined, True) and present_in_text(id_name, combined):
                if f"{id_name}.pdf" != base:
                    r = self.rename_file_safely(file_path, f"{id_name}.pdf", key, tag='identifier')
                    return r or file_path
                return file_path

        f_name = filename_as_name(base_no_ext)
        if f_name:
            f_name = standard_name(f_name)
            if len(f_name.split()) == 1 and len(f_name) >= 6:
                split = ai_split_blob(f_name)
                if split and sane_name(split) and valid_name(split, combined, True):
                    f_name = split
            if sane_name(f_name):
                if f"{f_name}.pdf" != base:
                    r = self.rename_file_safely(file_path, f"{f_name}.pdf", key, tag='filename')
                    return r or file_path
                return file_path

        fixed = standard_name(base_no_ext)
        if indicators and len(fixed.split()) >= 2 and sane_name(fixed) and valid_name(fixed, combined, False) and f"{fixed}.pdf" != base:
            r = self.rename_file_safely(file_path, f"{fixed}.pdf", key, tag='casefix')
            return r or file_path

        logging.info(f"{base}: no confident name -> left untouched (will retry on sweeps)")
        return None

    def handle_excel(self, file_path, key):
        base = os.path.basename(file_path)
        if base.lower().startswith('summary'):
            return file_path
        r = self.rename_file_safely(file_path, "Summary.xlsx", key, tag='excel')
        return r or file_path

    def rename_file_safely(self, old_path, new_file_name, key=None, tag=''):
        with self._lock:
            dir_name = os.path.dirname(old_path)
            old_base = os.path.basename(old_path)
            if new_file_name == old_base: return old_path

            existing = set()
            for f in os.listdir(dir_name):
                if f != old_base and os.path.isfile(os.path.join(dir_name, f)):
                    existing.add(f.lower())

            base, ext = os.path.splitext(new_file_name)
            candidate = new_file_name
            counter = 1
            while candidate.lower() in existing:
                candidate = f"{base}_{counter}{ext}"
                counter += 1

            if candidate == old_base: return old_path
            new_path = os.path.join(dir_name, candidate)
            try:
                rk = key if key is not None else file_key(old_path)
                self._rc[rk] = self._rc.get(rk, 0) + 1
                self._own.add(new_path)
                os.rename(old_path, new_path)
                self.stats['renamed'] += 1
                self._say(f"\n✅ RENAMED: {old_base} -> {candidate}  [{tag}]")
                logging.info(f"RENAMED: '{old_base}' -> '{candidate}' [{tag}]")
                return new_path
            except FileNotFoundError:
                logging.info(f"file disappeared before rename: {old_base}")
                return None
            except Exception as e:
                self._own.discard(new_path)
                self._say(f"\n⚠️ RENAME FAILED: {old_base}: {e}")
                logging.error(f"Rename failed: {str(e)}")
                return None

def main():
    global WATCH_FOLDER, LLM_MODEL, ENGINES
    print(f"📁 cvtool {VERSION}")
    print("   your offline CV-folder butler 🤖✨")
    if sys.platform != 'darwin':
        print("⚠️ cvtool runs best on macOS.")
        sys.exit(1)
    acquire_lock()
    ENGINES = set(detect_engines())
    if ENGINES:
        print(f"🔧 docx→pdf engines: {', '.join(sorted(ENGINES))}")
        if BROWSER_BIN: print(f"   browser: {BROWSER_BIN}")
        if LIBRE_BIN: print(f"   libre: {LIBRE_BIN}")
    else:
        print("⚠️ No docx→pdf engine found on this Mac.")
        print("   Fix: open the App Store, install the free 'Pages' app, open it once, then restart butler.")
    ensure_ocr()
    LLM_MODEL = get_model()
    if not LLM_MODEL:
        print("No AI model found. Open the Ollama app, then run: ollama pull llama3.2:1b")
        sys.exit(1)
    print("🤖 Warming up AI model (one-time, up to ~30s)…")
    try:
        ask_ai("Reply with the single word: ready")
    except Exception:
        pass

    print("\nDRAG & DROP the folder that CONTAINS your CVs (e.g. the JD position folder, or 06 Kabu), then press Return:")
    user_input = input("> ").strip().strip('"').strip("'").replace('\\', '')
    WATCH_FOLDER = os.path.normpath(os.path.expanduser(user_input))
    if not os.path.exists(WATCH_FOLDER):
        print(f"Error: Folder '{WATCH_FOLDER}' does not exist.")
        sys.exit(1)

    event_handler = CVOrganizer(WATCH_FOLDER)
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=True)
    observer.start()

    print("⏳ Scanning… (each dot = one file checked)")
    futures = []
    for root, dirs, files in os.walk(WATCH_FOLDER):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.startswith('.'): continue
            futures.append(event_handler.executor.submit(event_handler.process_file, os.path.join(root, file)))
    wait_interruptible(futures)
    print()
    print(f"✅ Scan complete · ✏️  renames: {event_handler.stats['renamed']}")
    print("👀 Watching silently… renames happen even while files are open (safe on macOS)")
    print("   (Ctrl+C to quit)\n")

    last_full = time.time(); last_hb = time.time(); n = 0
    try:
        while True:
            time.sleep(1)
            if time.time() - last_full > 20:
                last_full = time.time()
                for root, dirs, files in os.walk(WATCH_FOLDER):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        if file.startswith('.'): continue
                        event_handler.executor.submit(event_handler.process_file, os.path.join(root, file))
            if time.time() - last_hb > 120:
                last_hb = time.time(); n += 1
                print(f"💓 sweep #{n} · quiet · {event_handler.stats['renamed']} renamed total")
    except KeyboardInterrupt:
        observer.stop()
    finally:
        try: os.remove(LOCK_FILE)
        except Exception: pass
    observer.join()

if __name__ == "__main__":
    main()

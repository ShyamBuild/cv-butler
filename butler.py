try:
    import sys as _sysio; _sysio.stdout.reconfigure(line_buffering=True)  # LOG-FLUSH v81.8
except Exception:
    pass
import os, re, sys, time, logging, logging.handlers, json, subprocess, shutil, threading, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, wait
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pdfplumber, openpyxl
import cleaner
import briefing

logging.lastResort = logging.NullHandler()
import warnings
warnings.filterwarnings("ignore")
for _n in ("pdfminer", "fontTools"):
    _l = logging.getLogger(_n)
    _l.addHandler(logging.NullHandler())
    _l.setLevel(logging.CRITICAL)

VERSION = "butler v6 (final-rules edition)"
for _lf in sorted(__import__("glob").glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "butler_*.lock"))):
    try: print("   🔒 live lock: " + os.path.basename(_lf) + " -> " + open(_lf).read().strip())
    except Exception: pass
INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()  # HEADLESS-FIX v81.9: a log-file stdout means headless; loop, do not listen
if not INTERACTIVE:
    import builtins as _bi
    def _headless_input(prompt=''):
        time.sleep(2)
        return ''
    _bi.input = _headless_input  # HEADLESS-INPUT v81.11: no prompt may park or kill a headless loop

def _git_stamp():
    try:
        r = subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, timeout=5)
        return (r.stdout or '').strip() or 'nogit'
    except Exception:
        return 'nogit'
GIT_STAMP = _git_stamp()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(BASE_DIR, "butler.lock")
def _names_by_phone():
    try:
        import json as _j
        return _j.load(open(os.path.join(BASE_DIR, 'names_by_phone.json')))
    except Exception:
        return {}

def _xattr_raw(p, name='com.apple.metadata:_kMDItemUserTags'):  # XATTR-RAW v81.7
    try:
        import ctypes
        lc = ctypes.CDLL('/usr/lib/libc.dylib', use_errno=True)
        lc.getxattr.restype = ctypes.c_ssize_t
        lc.getxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]
        pb = p.encode() if isinstance(p, str) else p
        nb = name.encode() if isinstance(name, str) else name
        n = lc.getxattr(pb, nb, None, 0, 0, 0)
        if n <= 0: return b''
        buf = ctypes.create_string_buffer(n)
        n2 = lc.getxattr(pb, nb, buf, n, 0, 0)
        return buf.raw[:n2] if n2 > 0 else b''
    except Exception:
        return b''

def _sniff_ext(p):
    try:
        with open(p, 'rb') as f: h = f.read(8)
    except Exception:
        return None
    if h.startswith(b'%PDF'): return '.pdf'
    if h.startswith(b'PK\x03\x04'):
        try:
            import zipfile
            n = zipfile.ZipFile(p).namelist()
            if any(x.startswith('word/') for x in n): return '.docx'
            if any(x.startswith('xl/') for x in n): return '.xlsx'
        except Exception:
            return None
    if h.startswith(b'\xd0\xcf\x11\xe0'): return '.doc'
    return None

SETTLE_EXTS = ('.crdownload', '.part', '.partial', '.download', '.tmp', '.crdownload ')
def _settling(p):
    if SETTLE_TEST: return False
    try:
        b = os.path.basename(p).lower()
        if b.endswith(SETTLE_EXTS): return True
        st = os.stat(p)
        if st.st_size == 0: return True
        if (time.time() - st.st_mtime) >= 20: return False
        time.sleep(1.5)  # SETTLE-FAST v62: stability beats age
        st2 = os.stat(p)
        return st2.st_size != st.st_size or st2.st_mtime != st.st_mtime
    except Exception:
        return True
SETTLE_TEST = False
CONV_STATE = os.path.join(BASE_DIR, "converter_state.json")
OCRBIN = os.path.join(BASE_DIR, "cvocr")
SWIFT_SRC = os.path.join(BASE_DIR, "cvocr.swift")
OCR_SEM = threading.Semaphore(2)
CONV_SEM = threading.Semaphore(1)   # LibreOffice/Chrome are single-instance: conversions go one at a time
PHONES_FILE = os.path.join(BASE_DIR, "phones.json")
PHONE_RE = re.compile(r'(?:\+?91[\s\-\.]?)?([6-9](?:[\s\-\.]?\d){9})')
def phones_in_text(t):
    out = []
    for m in PHONE_RE.finditer(t or ''):
        d = re.sub(r'\D', '', m.group(1))
        if d not in out: out.append(d)
    return out
def phones_of(p):
    try: store = json.load(open(PHONES_FILE))
    except Exception: store = {}
    try:
        st = os.stat(p); k = f"{st.st_ino}|{st.st_mtime}|{st.st_size}"
    except OSError:
        return []
    e = store.get(os.path.abspath(p))
    if e and e.get('k') == k and e.get('phones') is not None: return e['phones']
    txt = ''
    try:
        with pdfplumber.open(p) as pdf:
            txt = "\n".join((pg.extract_text() or '') for pg in pdf.pages[:2])
    except Exception: pass
    if not txt.strip(): txt = extract_text_ocr(p)
    ph = phones_in_text(txt)
    store[os.path.abspath(p)] = {'k': k, 'phones': ph}
    try: json.dump(store, open(PHONES_FILE, 'w'))
    except Exception: pass
    return ph

_h = logging.handlers.RotatingFileHandler(os.path.join(BASE_DIR, "butler.log"), maxBytes=1_000_000, backupCount=3)
_h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log = logging.getLogger('butler'); log.setLevel(logging.INFO); log.addHandler(_h)

SWIFT_CODE = '''
import Foundation
import Vision
import PDFKit
import AppKit
func ocr(_ page: PDFPage) -> String {
    let ns = page.thumbnail(of: CGSize(width: 1500, height: 1950), for: .mediaBox)
    guard let cg = ns.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return "" }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["en-US"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do { try handler.perform([req])
        if let obs = req.results as? [VNRecognizedTextObservation] {
            return obs.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\\n") }
    } catch {}
    return ""
}
let args = CommandLine.arguments
guard args.count > 1, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else { exit(0) }
var pages: [String] = []
for i in 0..<min(doc.pageCount, 1) { if let p = doc.page(at: i) { pages.append(ocr(p)) } }
print(pages.joined(separator: "\\n"))
'''

def ensure_ocr():
    if os.path.exists(OCRBIN): return True
    if not shutil.which("swiftc"): return False
    try:
        with open(SWIFT_SRC, "w") as f: f.write(SWIFT_CODE)
        r = subprocess.run(["swiftc", "-O", "-o", OCRBIN, SWIFT_SRC], capture_output=True, timeout=600)
        return r.returncode == 0 and os.path.exists(OCRBIN)
    except Exception:
        return False

def extract_text_ocr(fp):
    if not os.path.exists(OCRBIN): return ""
    try:
        with OCR_SEM:
            r = subprocess.run([OCRBIN, fp], capture_output=True, text=True, timeout=180)
        return r.stdout or ""
    except Exception:
        return ""

def get_model(auto_open=True):
    for attempt in (0, 1):
        try:
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
                data = json.loads(r.read().decode())
            names = [m.get('name','') for m in data.get('models', []) if 'embed' not in m.get('name','').lower()]
            if names: return names[0]
        except Exception:
            pass
        if auto_open and attempt == 0:
            try:
                subprocess.run(['open', '-a', 'Ollama'], capture_output=True)
                print("🤖 Ollama was offline — opened it, waiting…")
                time.sleep(8)
            except Exception:
                break
    return None

LLM_MODEL = None
def ask_ai(prompt):
    payload = json.dumps({"model": LLM_MODEL, "messages": [{"role": "system", "content": "Strict JSON only."}, {"role": "user", "content": prompt}], "stream": False, "options": {"num_ctx": 2048}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())['message']['content']

def parse_ai_json(raw):
    if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw)

def compact_text(t):
    return re.sub(r'(?<=\b[A-Za-z]) (?=[A-Za-z]\b)', '', re.sub(r'([A-Za-z])\1{2,}', r'\1', t))

HONORIFICS = {'mr','mrs','ms','dr','prof','er','late','capt','sir'}
LABELS = {'name','contact','email','mobile','phone','address','dob'}
PARTICLES = {'van','von','der','den','de','la','le','di','da','el','al','bin','binte','ter','ten'}
BAD_WORDS = {'resume','curriculum','vitae','objective','career','summary','profile','cover','letter','application','portfolio','phone','email','contact','address','website','github','behance','dribbble','linkedin','location','pvt','ltd','llc','inc','corp','company','homes','pineapple','artstreet','sleepwell','kurlon','sheela','foam','sunsoft','technology','institute','university','college','school','board','senior','junior','strategy','driven','data','professional','permanent','present','notice','period','immediate','current','expected','lpa','ctc','years','experience','declaration','place','date','birth','gender','nationality','marital','status','languages','interests','father','mother','late','total','variable','digital','name','candidate','designation','position','dob','age','government','passionate','brief','highlights','qualification','qualifications','competencies','introduction','overview','snapshot','statement','skills','education','certifications','training','trainings','projects','achievements','expertise','hobbies','development','organization','growth','knowledge','graphic','designer','video','editor','motion','visual','animator','executive','manager','director','specialist','developer','engineer','analyst','consultant','intern','trainee','associate','seo','marketing','sales','hr','recruiter','content','writer','strategist','architect','planner','coordinator','officer','assistant','president','founder','ceo','cto','cfo','cmo','marketer','general','management','operations','operation','top','plant','unit','factory','works','division','corporate','department','team','mobile','supply','chain','logistics','procurement','purchase'}
LOCATION_WORDS = {'noida','greater','uttar','uttarakhand','delhi','mumbai','bengaluru','bangalore','hyderabad','chennai','kolkata','pune','gurgaon','gurugram','jaipur','lucknow','kanpur','meerut','ghaziabad','faridabad','agra','varanasi','patna','ranchi','jamshedpur','bhopal','indore','ahmedabad','surat','nagpur','nashik','thane','bihar','jharkhand','haryana','punjab','rajasthan','gujarat','maharashtra','pradesh','india','bharat','city','town','village','district','state','country','address','location','sector','phase','colony','society','street','road','nagar','marg','pincode','bijnor','haridwar','dehradun'}
FRAGMENTS = {'ign','inc','ltd','pvt','llc','hr','ui','ux','qa','mba','bba','bsc','msc','btech','mtech','phd','llb','bcom','mcom'}

SKILL_WORDS = {'technical','talent','acquisition','onboarding','recruitment','sourcing','screening','headhunting','partnering','partnership','engagement','retention','budgeting','hrms','sap','excel','powerpoint','communication','negotiation','leadership','teamwork','adaptability','creativity','production','planning','plant','quality','maintenance','engineering','operations','logistics','purchase','procurement','supply','chain','finance','accounts','audit','research','save','search','reports','resdex','naukri','alerts'}

JD_SIGNALS = ('job description', 'key responsibilities', 'responsibilities:', 'role & responsibilities', 'role and responsibilities', 'required qualifications', 'qualification required', 'experience required', 'about the company', 'company overview', 'job title', 'openings:', 'salary range', 'ctc range', 'walk-in', 'hiring for', 'looking for', 'urgent requirement', 'client details', 'desired candidate', 'eligibility')
CV_SIGNALS = ('career objective', 'professional summary', 'work experience', 'employment history', 'educational qualification', 'personal details', 'date of birth', 'declaration', 'curriculum vitae', 'father', 'resume')
STRONG_JD = ('job description', 'openings:', 'number of openings', 'salary range', 'ctc range', 'budget:', 'about the company', 'company overview', 'desired candidate', 'eligibility', 'walk-in', 'hiring for', 'looking for', 'urgent requirement')

LEARN_FILE = os.path.join(BASE_DIR, "learned_names.json")

def _learn_load():
    try: return json.load(open(LEARN_FILE))
    except Exception: return {}

def learn_name(key, display):
    d = _learn_load(); d[re.sub(r'[^a-z]', '', key.lower())] = display
    json.dump(d, open(LEARN_FILE, 'w'), indent=2)

def learned_for(name):
    if not name: return None
    return _learn_load().get(re.sub(r'[^a-z]', '', name.lower()))

MONTHS = {'jan','feb','mar','apr','may','jun','jul','aug','sep','sept','oct','nov','dec','january','february','march','april','june','july','august','september','october','november','december'}

def _junk(lt):
    if lt in BAD_WORDS or lt in LOCATION_WORDS or lt in FRAGMENTS or lt in SKILL_WORDS: return True
    for t in ('curriculum', 'vitae', 'resume', 'portfolio', 'coverletter', 'application'):
        if t in lt: return True
    for p in re.split(r'[^a-z]+', lt):
        if p and (p in BAD_WORDS or p in LOCATION_WORDS or p in FRAGMENTS or p in SKILL_WORDS): return True
    return False

def polish_name(name):
    name = re.sub(r'\s+', ' ', name.strip())
    if ',' in name:
        a, b = [x.strip() for x in name.split(',', 1)]
        if a and b: name = f"{b} {a}"
    toks = name.split(' ')
    while toks and toks[0].lower().rstrip('.,:') in HONORIFICS: toks.pop(0)
    return ' '.join(toks)

def standard_name(name):
    n = re.sub(r'[\/:*?"<>|]', '', polish_name(name or ''))
    n = re.sub(r'([a-z])([A-Z])', r'\1 \2', n)  # camelCase -> Camel Case
    n = n.strip().title()
    toks = n.split()
    for i in range(1, len(toks)):
        if toks[i].lower() in PARTICLES: toks[i] = toks[i].lower()
    return ' '.join(toks)

TEXT_CACHE = {}

def _cached_head(p):
    try:
        st = os.stat(p); ck = (st.st_ino, st.st_mtime, st.st_size)
    except OSError:
        return ''
    hit = TEXT_CACHE.get(ck)
    if hit: return hit[0][:2000].lower()
    try:
        import pdfplumber
        with pdfplumber.open(p) as _pdf:
            t = (_pdf.pages[0].extract_text() or '')
        TEXT_CACHE[ck] = (t, '')
        return t[:2000].lower()
    except Exception:
        return ''

def leading_name_run(line):
    out = []
    for t in line.split():
        core = t.rstrip('.,:')
        lt = core.lower()
        if not out and lt in HONORIFICS: continue
        if not out and lt in LABELS: continue
        if not core.isalpha(): break
        if _junk(lt): break
        if len(core) == 1 and not core.isupper(): break
        out.append(core)
        if len(out) >= 4: break
    return out

def sane_name(name):
    toks = name.split()
    if sum(1 for t in toks if len(t) == 1) >= 2: return False
    if not (1 <= len(toks) <= 4): return False
    for t in toks:
        if not (re.fullmatch(r'[A-Za-z][A-Za-z.\-]+', t) or (len(t) == 1 and t.isupper() and t != toks[0])): return False
        trans = sum(1 for a, b in zip(t, t[1:]) if a.islower() != b.islower())
        if trans > 3: return False
    if len(re.findall(r'([A-Za-z])\1', name)) >= 3: return False
    return True

def present_in_text(name, raw):
    low = raw.lower()
    toks = [t.lower().strip('.-') for t in name.split()]
    joined = ''.join(toks)
    for tt in toks:
        if len(tt) < 2: continue
        if not re.search(r'\b' + re.escape(tt) + r'\b', low):
            if not re.search(r'\b' + re.escape(joined) + r'\b', low):
                return False
    return True

def get_visual_name(fp):
    try:
        with pdfplumber.open(fp) as pdf:
            page = pdf.pages[0]
            words = page.extract_words(x_tolerance=3, y_tolerance=3, extra_attrs=["size"])
            if not words: return None
            top_words = [w for w in words if float(w['top']) < page.height * 0.20]
            if not top_words: return None
            mx = max(float(w['size']) for w in top_words)
            hw = sorted([w for w in top_words if float(w['size']) >= mx * 0.85], key=lambda w: (float(w['top']), float(w['x0'])))
            lines, cur, ct = [], [], -1
            for w in hw:
                if ct == -1 or abs(float(w['top']) - ct) < 5: cur.append(w); ct = float(w['top'])
                else: lines.append(cur); cur = [w]; ct = float(w['top'])
            if cur: lines.append(cur)
            parsed = [(" ".join(w['text'] for w in ws), max(float(w['size']) for w in ws)) for ws in lines]
            for i, (clean, size) in enumerate(parsed):
                run = leading_name_run(compact_text(clean))
                if 2 <= len(run) <= 4 and sum(len(t) for t in run) >= 6:
                    if all(t[:1].isupper() for t in run) or clean.isupper(): return ' '.join(run)
                if len(run) == 1 and run[0].isalpha() and len(run[0]) >= 5 and (run[0].isupper() or run[0].istitle()):
                    if i + 1 < len(parsed):
                        nr = leading_name_run(compact_text(parsed[i+1][0]))
                        if len(nr) == 1 and nr[0].isalpha() and len(nr[0]) >= 3 and parsed[i+1][1] >= size * 0.8:
                            return f"{run[0]} {nr[0]}"
                    return run[0]
            return None
    except Exception:
        return None

def heuristic_name(text):
    for line in [l.strip() for l in text.split('\n') if l.strip()][:8]:
        run = leading_name_run(compact_text(line))
        if 2 <= len(run) <= 4 and sum(len(t) for t in run) >= 6:
            j = ' '.join(run)
            if j.isupper() or j.istitle(): return j
    return None

def _mdfind_app(bid):
    try:
        r = subprocess.run(["mdfind", f"kMDItemCFBundleIdentifier == '{bid}'"], capture_output=True, text=True, timeout=15)
        for line in (r.stdout or "").splitlines():
            if line.strip() and os.path.exists(line.strip()): return line.strip()
    except Exception: pass
    return None

def detect_engines():
    eng = []
    libre = shutil.which("soffice")
    for lp in ("/Applications/LibreOffice.app/Contents/MacOS/soffice",
               os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice")):
        if not libre and os.path.exists(lp): libre = lp
    if not libre: libre = _mdfind_app('org.libreoffice.script')
    if libre:
        if libre.endswith('.app'): libre = os.path.join(libre, "Contents/MacOS/soffice")
        eng.append(('libreoffice', libre))
    pages = None
    for pp in ("/Applications/Pages.app", "/System/Applications/Pages.app",
               os.path.expanduser("~/Applications/Pages.app")):
        if os.path.exists(pp): pages = pp; break
    if not pages: pages = _mdfind_app('com.apple.iWork.Pages')
    if not pages:
        try:
            r = subprocess.run(['osascript', '-e', 'POSIX path of (path to application "Pages")'], capture_output=True, text=True, timeout=10)
            cand = (r.stdout or '').strip().rstrip('/')
            if r.returncode == 0 and cand and os.path.isdir(cand): pages = cand
        except Exception:
            pass
    if pages: eng.append(('pages', pages))
    browser = None
    for bp in ("/Applications/Google Chrome.app", "/Applications/Microsoft Edge.app",
               "/Applications/Brave Browser.app",
               os.path.expanduser("~/Applications/Google Chrome.app")):
        if os.path.exists(bp): browser = bp; break
    if not browser:
        browser = _mdfind_app('com.google.Chrome') or _mdfind_app('com.microsoft.edgemac') or _mdfind_app('com.brave.Browser')
    if browser:
        if browser.endswith('.app'):
            browser = os.path.join(browser, "Contents/MacOS", os.path.splitext(os.path.basename(browser))[0])
        eng.append(('html-pdf', browser))
    return eng

def convert_doc(doc_path, pdf_path, engines):
    try:
        if os.path.getsize(doc_path) == 0:
            print('⚠️ conversion skipped: source is 0 bytes (still downloading?)')
            return False
    except Exception:
        return False
    for name, binp in engines:
        try:
            if name == 'libreoffice':
                out_dir = os.path.dirname(pdf_path)
                subprocess.run([binp, "--headless", "-env:UserInstallation=file:///tmp/cvtool_lo_profile", "--convert-to", "pdf", "--outdir", out_dir, doc_path], capture_output=True, timeout=120)
                gen = os.path.join(out_dir, os.path.splitext(os.path.basename(doc_path))[0] + ".pdf")
                if os.path.exists(gen):
                    if gen != pdf_path: os.replace(gen, pdf_path)
                    return True
            elif name == 'pages':
                sc = f'tell application "Pages"\nset theDoc to open POSIX file "{doc_path}"\nexport theDoc to POSIX file "{pdf_path}" as PDF\nclose theDoc saving no\nend tell'
                subprocess.run(["osascript", "-e", sc], capture_output=True, timeout=120)
                if os.path.exists(pdf_path): return True
            elif name == 'html-pdf':
                hp = pdf_path + ".tmp.html"
                subprocess.run(["textutil", "-convert", "html", "-output", hp, doc_path], capture_output=True, timeout=60)
                if os.path.exists(hp):
                    try:
                        url = "file://" + urllib.parse.quote(hp)
                        subprocess.run([binp, "--headless", "--disable-gpu", "--no-sandbox", "--user-data-dir=/tmp/cvtool_browser_profile", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", url], capture_output=True, timeout=120)
                    except Exception:
                        pass
                    finally:
                        try: os.remove(hp)
                        except Exception: pass
                    if os.path.exists(pdf_path): return True
        except Exception as e:
            log.error(f"engine {name} failed: {e}")
    return False

def convert_pages(p, pdf_path):
    import subprocess
    if not os.path.exists('/Applications/Pages.app'): return False
    def esc(x): return x.replace('\\', '\\\\').replace('"', '\\"')
    script = ('tell application "Pages"\n'
              '  set d to open POSIX file "' + esc(p) + '"\n'
              '  export d to POSIX file "' + esc(pdf_path) + '" as PDF\n'
              '  close d saving no\n'
              'end tell\n')
    try:
        r = subprocess.run(['osascript', '-e', script], capture_output=True, timeout=180)
        okp = r.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0
        if not okp:
            try: log.error(f"pages failed {os.path.basename(p)}: rc={r.returncode} {r.stderr.decode()[:300]}")
            except Exception: pass
        return okp
    except Exception as e:
        try: log.error(f"pages exception {os.path.basename(p)}: {e}")
        except Exception: pass
        return False

def convert_eml(p, pdf_path, engines):
    import email as _em, html as _hl
    try:
        m = _em.message_from_file(open(p, encoding='utf-8', errors='ignore'))
        parts = []
        if m.is_multipart():
            for pr in m.walk():
                pay = pr.get_payload(decode=True)
                if not pay: continue
                t = pay.decode('utf-8', 'ignore')
                if pr.get_content_type() == 'text/plain': parts.append(t)
                elif pr.get_content_type() == 'text/html': parts.append(re.sub(r'<[^>]+>', ' ', t))
        else:
            pay = m.get_payload(decode=True)
            if pay: parts.append(pay.decode('utf-8', 'ignore'))
        body = (m.get('Subject', '') or '') + "\n\n" + "\n".join(parts)
        hp = pdf_path + ".tmp.html"
        with open(hp, 'w') as f: f.write("<html><body><pre>" + _hl.escape(body) + "</pre></body></html>")
        for binp in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                     "/Applications/Chromium.app/Contents/MacOS/Chromium"):
            if os.path.exists(binp):
                subprocess.run([binp, "--headless", "--disable-gpu", "--no-sandbox",
                                f"--print-to-pdf={pdf_path}", hp], capture_output=True, timeout=120)
                break
        try: os.remove(hp)
        except Exception: pass
        return os.path.exists(pdf_path)
    except Exception:
        return False

def convert_msg(msg_path, pdf_path, engines):
    try:
        import extract_msg
    except Exception:
        log.error("extract-msg not installed")
        return False
    try:
        msg = extract_msg.Message(msg_path)
        body = msg.htmlBody
        if not body:
            body = f"<html><body><h2>{msg.subject}</h2><p><b>From:</b> {msg.sender}</p><hr><pre>{msg.body or ''}</pre></body></html>".encode()
        if isinstance(body, bytes): body = body.decode('utf-8', errors='ignore')
        hp = pdf_path + ".tmp.html"
        with open(hp, 'w', encoding='utf-8') as f: f.write(body)
        browser = next((b for n, b in engines if n == 'html-pdf'), None)
        if not browser: return False
        url = "file://" + urllib.parse.quote(hp)
        subprocess.run([browser, "--headless", "--disable-gpu", "--no-sandbox", "--user-data-dir=/tmp/cvtool_browser_profile", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", url], capture_output=True, timeout=120)
        try: os.remove(hp)
        except Exception: pass
        return os.path.exists(pdf_path)
    except Exception as e:
        log.error(f"msg convert failed: {e}")
        return False

COLOR_TAGS = {'Red','Orange','Yellow','Green','Blue','Purple','Gray','Grey'}
TAG_NAMES = {'Rejected by Client','Awaiting JD Confirmation','Awaiting CV Update','Ready for Manager Review','Call Scheduled','Closed – Not Proceeding','Closed - Not Proceeding','Interview Today','Interview Tomorrow','Interview Scheduled','Interview Cleared','Expected to Join','Joined - Payment Pending','Joined – Payment Pending','Feedback Pending','Payment Received','Position Active','Position On Hold','Position Closed'}
def _tags_of_fast(p):
    try:
        import plistlib
        arr = plistlib.loads(_xattr_raw(p, 'com.apple.metadata:_kMDItemUserTags'))
        out = [str(t).split(chr(10))[0].strip() for t in arr]
        return [t for t in out if t and t not in COLOR_TAGS]
    except Exception:
        return None
def _has_tag_xattr(p):
    t = _tags_of_fast(p)
    if t is None: return False
    return any(x in TAG_NAMES or x.replace(chr(8211), '-') in TAG_NAMES for x in t)

def _tags_from_plist(path):
    try:
        import plistlib
        data = _xattr_raw(path, 'com.apple.metadata:_kMDItemUserTags')
        out = []
        def walk(o):
            if isinstance(o, str):
                nm = o.split(chr(10))[0].strip()
                if nm and nm not in COLOR_TAGS: out.append(nm)
            elif isinstance(o, (list, tuple)):
                for x in o: walk(x)
        walk(plistlib.loads(data))
        return out
    except Exception:
        return None





def _unescape(s):
    BS = chr(92) + chr(92)
    s = re.sub(BS + 'U([0-9a-fA-F]{4,8})', lambda m: chr(int(m.group(1), 16)), s)
    s = re.sub(BS + 'u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    s = s.replace(chr(92) + '"', '"')
    return s
def get_tags(path):
    try:
        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)
        out = (r.stdout or '').strip()
        if not out or '(null)' in out: return []
        raw = re.findall(r'"([^"]*)"', out)
        if not raw:
            raw = [x.strip().rstrip(',') for x in out.splitlines()[1:] if x.strip().rstrip(',') not in ('(', ')')]
        tags = []
        for item in raw:
            nm = _unescape(item).split(chr(10))[0].strip()
            if nm and nm not in COLOR_TAGS and nm not in tags: tags.append(nm)
        return tags
    except Exception:
        return []

class StageLog:
    def __init__(self, root):
        self.path = os.path.join(root, 'stage_log.json')
        self.data = {}
        try:
            if os.path.exists(self.path):
                self.data = json.load(open(self.path))
        except Exception:
            self.data = {}
    def _save(self):
        try:
            tmp = self.path + '.tmp'
            json.dump(self.data, open(tmp, 'w'), indent=2)
            os.replace(tmp, self.path)
        except Exception:
            pass
    def _n(self, s): return (s or '').strip().lower()
    def observe(self, name, stage, position):
        k = self._n(name)
        if not k or not stage: return
        cur = self.data.get(k, [])
        if cur and cur[-1].get('stage') == stage and cur[-1].get('position') == position: return
        cur.append({'stage': stage, 'position': position, 'ts': int(time.time())})
        self.data[k] = cur[-50:]
        self._save()
    def latest(self, name):
        cur = self.data.get(self._n(name), [])
        return cur[-1] if cur else None
    def all_for(self, name):
        return list(reversed(self.data.get(self._n(name), [])))

class Butler:
    RULES_VERSION = 'v19-fresh-eyes'
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.engines = sorted(detect_engines(), key=lambda e: 0 if e[0] == 'pages' else 1)  # Pages first (best fidelity); libreoffice/html remain automatic fallbacks
        self.conv_state = self._load()
        self.stats = {'converted': 0, 'renamed': 0, 'moved': 0}
        self.rc = {}
        self.busy = set()
        try:
            with open(os.path.join(BASE_DIR, "name_locks.json")) as f:
                self.locks = {x.lower() for x in json.load(f)}
        except Exception:
            self.locks = set()
        self.lock = threading.Lock()
        self.slog = StageLog(root)

    def _load(self):
        try:
            with open(CONV_STATE) as f: return json.load(f)
        except Exception: return {}

    def _save(self):
        try:
            with open(CONV_STATE, "w") as f: json.dump(self.conv_state, f, indent=2)
        except Exception: pass

    def position_folder_for(self, p):
        dd = os.path.dirname(os.path.abspath(p))
        rel = os.path.relpath(dd, self.root)
        parts = [] if rel == '.' else rel.split(os.sep)
        if len(parts) >= 2:
            return os.path.join(self.root, parts[0], parts[1])
        return dd

    def _save_idx(self):
        if not getattr(self, 'scan_idx', None): return
        try:
            json.dump({'root': self.root, 'at': time.time(),
                       'idx': getattr(self, 'scan_idx', {}),
                       'ino': getattr(self, 'scan_ino', {})},
                      open(_idx_path(self.root), 'w'))
        except Exception:
            pass

    def _rename(self, old_path, new_name, say, tag):
        _selfb = os.path.basename(old_path).lower()  # SELF-FREE v65
        _bn, _be = os.path.splitext(new_name)
        if (_bn + _be).lower() == _selfb: return  # SELF-FREE v65
        if _settling(old_path): return  # RENAME-GATE v61
        d = os.path.dirname(old_path); ob = os.path.basename(old_path)
        if not os.path.exists(old_path): return
        if new_name == ob: return
        existing = {f.lower() for f in os.listdir(d) if f != ob and os.path.isfile(os.path.join(d, f))}
        b, e = os.path.splitext(new_name); cand, c = new_name, 1
        while cand.lower() in existing: cand, c = f"{b}_{c}{e}", c + 1
        if cand == ob: return
        try:
            os.rename(old_path, os.path.join(d, cand))
            with self.lock: self.stats['renamed'] += 1
            say(f"\n✏️ [rename] {ob} -> {cand}  [{tag}]")
            si = getattr(self, 'scan_idx', None)
            if si:
                np_ = os.path.join(d, cand)
                for k, v in list(si.items()):
                    if v == old_path: si[k] = np_
                self._save_idx()
        except Exception as ex:
            say(f"\n⚠️ [rename] failed: {ob}: {ex}")
            return
        src = getattr(self, '_pending_src', {}).pop(os.path.abspath(old_path), None)
        if src: self._archive_source(src, say, new_base=os.path.splitext(cand)[0])

    def _compact_numbers(self, folder, say):
        if not os.path.isdir(folder): return
        for f in sorted(os.listdir(folder)):
            fp = os.path.join(folder, f)
            if not os.path.isfile(fp): continue
            b, e = os.path.splitext(f)
            m = re.match(r'^(.*?)\s*\((\d+)\)$', b) or re.match(r'^(.*?)\s+(\d+)$', b)
            if not m: continue
            base, num = m.group(1).strip(), m.group(2)
            if not base: continue
            target = f"{base}_{num}{e}"
            if target == f: continue
            if os.path.exists(os.path.join(folder, target)): continue
            self._rename(fp, target, say, 'suffix-canonical')
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith(".pdf"):
                try: self.normalize_suffix(os.path.join(folder, f), say)
                except Exception: pass
        fam = {}
        for f in sorted(os.listdir(folder)):
            fp = os.path.join(folder, f)
            if not os.path.isfile(fp) or f.lower().endswith(".pdf"): continue
            b, e = os.path.splitext(f)
            m = re.match(r'^(.*?)[ _](\d+)$', b) or re.match(r'^(.*?)\((\d+)\)$', b)
            key = ((m.group(1).strip() if m else b), e.lower())
            fam.setdefault(key, []).append((0 if not m else int(m.group(2)), f))
        for (base, e), items in fam.items():
            if base.lower() in self.locks: continue
            numbered = sorted([(n, f) for n, f in items if n])
            if not numbered: continue
            plain = os.path.join(folder, base + e)
            if not os.path.exists(plain):
                n0, f0 = numbered[0]
                self._rename(os.path.join(folder, f0), base + e, say, "compact")
            cur = {}
            for f in os.listdir(folder):
                b2, e2 = os.path.splitext(f)
                m2 = re.match(r'^(.*?)[ _](\d+)$', b2) or re.match(r'^(.*?)\((\d+)\)$', b2)
                if m2 and m2.group(1).strip() == base and e2.lower() == e:
                    cur[int(m2.group(2))] = f
            for expect in range(1, len(cur) + 1):
                if expect in cur: continue
                act = min((x for x in cur if x > expect), default=None)
                if act is None: break
                self._rename(os.path.join(folder, cur[act]), f"{base}_{expect}{e}", say, "compact")
                del cur[act]; cur[expect] = f"{base}_{expect}{e}"

    def _check_siblings(self, folder):
        if not os.path.isdir(folder): return
        try:
            self._compact_numbers(folder, print)
        except Exception as e:
            print(f"⚠️ compact error in {folder}: {e}")

    def normalize_suffix(self, p, say):
        if _settling(p): return p  # NORM-GATE v61
        base = os.path.basename(p)
        if base.lower() in self.locks: return p
        m = (re.match(r'^(.*)_(\d+)\.pdf$', base, re.I)
             or re.match(r'^(.*)\s*\((\d+)\)\.pdf$', base, re.I)
             or re.match(r'^(.*?)\s*copy(?:\s*(\d+))?\.pdf$', base, re.I))
        if not m: return p
        clean = m.group(1).strip()
        if not clean: return p
        cur = int(m.group(2) or 1)
        dd = os.path.dirname(p)
        v = get_visual_name(p)
        if not v or standard_name(v).lower() != standard_name(clean).lower(): return p
        target = None
        for newn in range(0, cur):
            c = os.path.join(dd, clean + '.pdf') if newn == 0 else os.path.join(dd, clean + '_%d.pdf' % newn)
            if not os.path.exists(c): target = c; break
        if not target: return p
        try:
            os.rename(p, target)
            with self.lock: self.stats['renamed'] += 1
            say('\n✏️ [rename] ' + base + ' -> ' + os.path.basename(target) + '  [cleanup]')
            return target
        except Exception as ex:
            say('\n⚠️ [rename] failed: ' + base + ': ' + str(ex))
        return p

    def _archive_source(self, p, say, new_base=None):
        try:
            P = os.path.dirname(os.path.abspath(p))
            if new_base:
                bb, ee = os.path.splitext(os.path.basename(p))
                np_ = os.path.join(P, f"{new_base}{ee}")
                if not os.path.exists(np_):
                    os.rename(p, np_); p = np_
            arch = P if os.path.basename(P).lower() in ('converted doc files', 'converted files') else os.path.join(P, "Converted Files")
            os.makedirs(arch, exist_ok=True)
            dest = os.path.join(arch, os.path.basename(p))
            if os.path.abspath(p) == os.path.abspath(dest): return
            if os.path.exists(dest):
                bb, ee = os.path.splitext(os.path.basename(p)); c = 1
                while os.path.exists(dest): dest, c = os.path.join(arch, f"{bb}_{c}{ee}"), c + 1
            shutil.move(p, dest)
            say(f"\n🗂 [archive] {os.path.basename(p)} -> Converted Files/")
        except Exception as ex:
            say(f"\n⚠️ [archive] failed: {os.path.basename(p)}: {ex}")

    def handle_convert(self, p, say):
        ext = os.path.splitext(p)[1].lower()
        try:
            st = os.stat(p); key = f"{st.st_ino}|{st.st_size}"
        except OSError:
            return None
        with self.lock:
            already = self.conv_state.get(p) == key
        if already:
            pp = os.path.splitext(p)[0] + ".pdf"
            if os.path.exists(pp) and os.path.basename(os.path.dirname(p)).lower() not in ('converted doc files', 'converted files'):
                self._archive_source(p, say, new_base=os.path.splitext(os.path.basename(pp))[0])
                if os.path.exists(p): self._no_cache = True
            return None
        _pd = os.path.dirname(os.path.abspath(p))
        if os.path.basename(_pd).lower() in ('converted doc files', 'converted files'):
            _pd = os.path.dirname(_pd)
        pdf_path = os.path.join(_pd, os.path.splitext(os.path.basename(p))[0] + ".pdf")
        pdf_exists = os.path.exists(pdf_path)
        fresh = False
        if pdf_exists:
            try:
                fresh = st.st_mtime > os.stat(pdf_path).st_mtime + 5
            except OSError:
                fresh = False
        if pdf_exists and not fresh:
            if not already:
                with self.lock: self.conv_state[p] = key; self._save()
            self._archive_source(p, say, new_base=os.path.splitext(os.path.basename(pdf_path))[0])
            if os.path.exists(p): self._no_cache = True
            return pdf_path
        if self.conv_state.get('fail:' + p, 0) >= 3: return None
        say(f"\n⚙️ [convert] {os.path.basename(p)} …")
        with CONV_SEM:
            eng = '?'
            if ext in ('.msg', '.eml'):
                ok = (convert_msg if ext == '.msg' else convert_eml)(p, pdf_path, self.engines); eng = 'mail'
            else:
                ok = convert_pages(p, pdf_path); eng = 'pages'
                if not ok:
                    ok = convert_doc(p, pdf_path, [e for e in self.engines if not (e == 'libreoffice' and '|' in p)]); eng = 'libre'
            if not ok:
                ok = os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0
                if ok: eng = 'rescued'
        if ok:
            say(f"\n📄 [convert·{eng}] {os.path.basename(p)} -> {os.path.basename(pdf_path)}")
            try: os.remove(pdf_path + '.tmp.html')
            except Exception: pass
            with self.lock:
                self.conv_state[p] = key; self.conv_state.pop('fail:' + p, None); self.stats['converted'] += 1; self._save()
            self._pending_src = getattr(self, '_pending_src', {})
            self._pending_src[os.path.abspath(pdf_path)] = p
            if ext in ('.msg', '.eml'):
                self._email_pdf = getattr(self, '_email_pdf', {})
                self._email_pdf[os.path.abspath(pdf_path)] = True
            return pdf_path
        with self.lock:
            self.conv_state['fail:' + p] = self.conv_state.get('fail:' + p, 0) + 1; self._save()
            if self.conv_state['fail:' + p] < 3:
                self._no_cache = True
        say(f"\n⚠️ [convert] failed: {os.path.basename(p)} (no working engine) - attempt {self.conv_state['fail:' + p]}/3")
        return None

    def _llm_json(self, prompt):
        try:
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
                models = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]
            if not models: return None
            payload = json.dumps({"model": models[0], "messages": [{"role": "user", "content": prompt}], "stream": False}).encode()
            req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = json.loads(r.read().decode())['message']['content']
            raw = raw.strip()
            if '```' in raw: raw = raw.split('```')[1]
            if raw.lower().startswith('json'): raw = raw[4:]
            m = re.search(r'\{.*\}', raw, re.S)
            return json.loads(m.group(0) if m else raw)
        except Exception:
            return None

    def _jload(self):
        self.journal = {}
        try:
            self.journal = json.load(open(os.path.join(BASE_DIR, 'butler_journal.json')))
        except Exception:
            pass
        if len(self.journal) > 20000: self.journal = {}

    def _jsave(self):
        try:
            json.dump(self.journal, open(os.path.join(BASE_DIR, 'butler_journal.json'), 'w'))
        except Exception:
            pass

    def _jkey(self, p):
        try:
            import zlib
            st = os.stat(p)
            try:
                tg = _xattr_raw(p, 'com.apple.metadata:_kMDItemUserTags')
            except Exception:
                tg = b''
            return [round(st.st_mtime, 3), st.st_size, zlib.crc32(tg), self.RULES_VERSION, os.path.basename(p).lower()]
        except OSError:
            return None

    def _is_jd(self, base, head):
        bl = base.lower()
        if bl.startswith('jd') or '_jd' in bl or ' jd' in bl or bl.endswith('jd.pdf') or 'job description' in bl: return True
        jd = sum(1 for x in JD_SIGNALS if x in head)
        cv = sum(1 for x in CV_SIGNALS if x in head)
        strong = any(x in head for x in STRONG_JD)
        return strong and jd >= 2 and cv == 0   # only unmistakable JDs

    def _rename_jd(self, p, base, head, say):
        cur = os.path.splitext(base)[0]
        new = cur
        new = re.sub(r'\s*[\(\[]\d+[\)\]]\s*$', '', new)          # (1) [2]
        new = re.sub(r'\s+copy\s*\d*$', '', new, flags=re.I)        # " copy" / " copy 2"
        new = re.sub(r'\s*[_\-]\s*copy\s*\d*$', '', new, flags=re.I)
        new = re.sub(r'\s{2,}', ' ', new).strip(' -_')                # double spaces / edge junk
        if new and new != cur:
            self._rename(p, f"{new}.pdf", say, 'jd-clean')

    def handle_pdf(self, p, say):
        base = os.path.basename(p)
        bl = base.lower()
        if bl.startswith('jd') or '_jd' in bl or ' jd' in bl or bl.endswith('jd.pdf'):
            src = getattr(self, '_pending_src', {}).pop(os.path.abspath(p), None)
            if src: self._archive_source(src, say, new_base=os.path.splitext(base)[0])
            if src and os.path.exists(src): self._no_cache = True
            return
        if 'application form' in bl or 'resdex' in bl or 'save search' in bl:
            src = getattr(self, '_pending_src', {}).pop(os.path.abspath(p), None)
            if src: self._archive_source(src, say, new_base=os.path.splitext(base)[0])
            if src and os.path.exists(src): self._no_cache = True
            return
        head = _cached_head(p)
        if self._is_jd(base, head) or getattr(self, '_email_pdf', {}).pop(os.path.abspath(p), None):
            self._rename_jd(p, base, head, say)
            src = getattr(self, '_pending_src', {}).pop(os.path.abspath(p), None)
            if src: self._archive_source(src, say, new_base=os.path.splitext(base)[0])
            if src and os.path.exists(src): self._no_cache = True
            return
        if bl.startswith(('screencapture', 'subject', 'fw', 'forwarded', 'whatsapp', 'img_', 'scan_', 'attachment')): return
        if base.lower() in self.locks: return  # user-locked name: never touch
        if not os.path.isfile(p): return
        NL = chr(10)
        try:
            _st = os.stat(p); _ck = (_st.st_ino, _st.st_mtime, _st.st_size)
        except OSError:
            _ck = None
        _hit = TEXT_CACHE.get(_ck) if _ck else None
        if _hit and _hit[1]:
            text, wtext = _hit[0], _hit[1]
        else:
            try:
                with pdfplumber.open(p) as pdf:
                    pgs = pdf.pages[:2]
                    text = NL.join(pg.extract_text() or "" for pg in pgs)
                    wtext = " ".join(w['text'] for pg in pgs for w in (pg.extract_words(extra_attrs=["size"]) or []))
                if _ck: TEXT_CACHE[_ck] = (text, wtext)
            except Exception:
                text = ""; wtext = ""
        if not text.strip(): text = extract_text_ocr(p)
        if not text.strip() and not wtext.strip(): return
        ctext = NL.join(compact_text(l) for l in text.split(NL))
        hay = ctext + NL + compact_text(wtext)
        ino = None
        try: ino = os.stat(p).st_ino
        except OSError: pass
        if ino is not None and getattr(self, 'rcn', {}).get(ino) != base:
            self.rcn = getattr(self, 'rcn', {}); self.rcn[ino] = base; self.rc[ino] = 0
        if ino is not None and self.rc.get(ino, 0) >= 2:
            return  # loop breaker

        def ok(name):
            return (bool(name) and bool(name.split())
                    and name.split()[0].lower() not in BAD_WORDS
                    and not (set(name.lower().split()) & LOCATION_WORDS)
                    and not (set(name.lower().split()) & FRAGMENTS)
                    and sane_name(name) and present_in_text(name, hay))

        def ask_name():
            if not LLM_MODEL: return None
            try:
                prompt = f'''Extract the candidate's PERSONAL FULL NAME from this CV text. Ignore labels like 'Name:', job titles, companies, document titles, and EMAIL HANDLES. Return ONLY JSON {{"name": "..."}}. Text: {ctext[:1500]}'''
                d = parse_ai_json(ask_ai(prompt))
                return standard_name(d.get('name', ''))
            except Exception:
                return None

        def split_blob(name):
            if not (name and len(name.split()) == 1
                    and (len(name) >= 12 or (len(name) >= 10 and f"{name}.pdf" == base))):
                return name
            if not LLM_MODEL: return name
            try:
                prompt = f'''The string '{name}' is a person's full name written without proper spacing. Insert the correct space(s) using ONLY the letters present - do NOT add or invent words. Write it in Title Case (example: 'jatinchauhan' -> 'Jatin Chauhan'). Return ONLY JSON {{"name": "..."}}.'''
                d = parse_ai_json(ask_ai(prompt))
                a2 = standard_name(d.get('name', ''))
                return a2 if (a2 and len(a2.split()) >= 2 and ok(a2)) else name
            except Exception:
                return name


        vv = None


        if _ck:


            _h = TEXT_CACHE.get(_ck)


            if _h and len(_h) >= 3: vv = _h[2]


        if vv is None:


            vv = get_visual_name(p)


            if _ck: TEXT_CACHE[_ck] = (text, wtext, vv)
        vv = standard_name(vv) if vv else None
        vv = split_blob(vv) if ok(vv) else None
        hh = heuristic_name(ctext)
        hh = standard_name(hh) if hh else None
        hh = split_blob(hh) if ok(hh) else None
        # OCR FALLBACK (systemic): a garbage/partial text layer must never blind
        # the renamer - if no engine found a name, ask Vision OCR once (cached).
        if vv is None and hh is None and _ck not in getattr(self, '_ocr_done', set()):
            self._ocr_done = getattr(self, '_ocr_done', set()); self._ocr_done.add(_ck)
            _ocr = extract_text_ocr(p)
            if _ocr.strip():
                if _ck: TEXT_CACHE[_ck] = (_ocr, wtext)
                text = _ocr
                ctext = NL.join(compact_text(l) for l in text.split(NL))
                hay = ctext + NL + compact_text(wtext)
                hh = heuristic_name(ctext)
                hh = standard_name(hh) if hh else None
                hh = split_blob(hh) if ok(hh) else None

        # CONFLICT ARBITRATION: the header is the default authority, but when a
        # text candidate contradicts it, corroboration decides - a text name wins
        # ONLY with >=2 independent supports AND strictly more than the header.
        # Ties and doubts go to the header (it is the declared name).
        def corrob(name):
            if not name: return 0
            low = name.lower()
            c = sum(1 for l in ctext.split(NL) if low in l.lower())
            joined = ''.join(low.split())
            if re.search(r'\b' + re.escape(joined) + r'\b', ctext.lower()): c += 1
            return c

        name = tag = None
        if vv and hh and vv != hh:
            ch = corrob(hh)   # AI deliberately NOT counted: it reads the same text
            cv = corrob(vv)
            if ch >= 2 and ch > cv:
                name, tag = hh, 'arbitrated'
            else:
                name, tag = vv, 'visual'
        elif vv:
            name, tag = vv, 'visual'
        elif hh:
            aa = ask_name(); aa = aa if ok(aa) else None
            if aa and aa == hh:
                name, tag = hh, 'consensus'
            else:
                name, tag = hh, 'text'
        else:
            aa = ask_name(); aa = aa if ok(aa) else None
            if aa: name, tag = aa, 'ai'
        def _mutilated(bn, cand):
            bt = os.path.splitext(bn)[0].split(); ct = cand.split()
            if len(bt) != len(ct) or len(bt) < 2: return False
            return all(c.lower() == b[1:].lower() or b.lower() == c[1:].lower() or (abs(len(b) - len(c)) == 1 and (c.lower() in b.lower() or b.lower() in c.lower())) for b, c in zip(bt, ct))
        lz = learned_for(vv or hh)
        if lz and (not name or re.sub(r'[^a-z]', '', name.lower()) != re.sub(r'[^a-z]', '', lz.lower())):
            name, tag = lz, 'learned'
        if name:
            tk = name.split()
            if len(tk) == 1 and (tk[0].lower() in MONTHS or len(tk[0]) < 4):
                name = None  # 'Jan'-style hallucinations are never person names
            else:
                bc = re.sub(r'[\s_(-]*\d+[)\s_]*$', '', os.path.splitext(base)[0])
                if re.sub(r'[^a-z]', '', name.lower()) == re.sub(r'[^a-z]', '', bc.lower()) and ' ' in bc:
                    name = None  # already human-formatted equivalent - keep current
        if name and _mutilated(base, name):
            name = None  # broken-font reading of an already-good name: keep current
        if name and re.sub(r'\s', '', name.lower()) == re.sub(r'\s', '', os.path.splitext(base)[0].lower()):
            name = None  # same letters, only spacing differs: current name is fine
        _nbm = _names_by_phone()  # NAME-BY-PHONE v79
        _st0 = os.path.splitext(base)[0]
        _phs = []
        if name and (_nbm or _st0 != name):
            try:
                _phs = phones_of(p) or []
            except Exception:
                _phs = []
        if _nbm:
            for _d in _phs:
                if _d in _nbm: name = _nbm[_d]; break
        if name and _phs and _st0 != name and len(_st0.split()) >= 2 and all(w[:1].isupper() for w in _st0.split() if w):  # LEARN-BACK v80.1
            for _d in _phs: _nbm[_d] = _st0
            try:
                import json as _j2
                _j2.dump(_nbm, open(os.path.join(BASE_DIR, 'names_by_phone.json'), 'w'), indent=1)
            except Exception: pass
            name = _st0
        _b0 = os.path.splitext(base)[0]  # SUFFIX-STABLE v65
        _okb = (not name) or _b0.lower() == name.lower() or bool(re.match(re.escape(name) + r'[_\s]\d+$', _b0, re.I))
        if name and not _okb:
            if ino is not None: self.rc[ino] = self.rc.get(ino, 0) + 1
            self._rename(p, f"{name}.pdf", say, tag)
        src = getattr(self, '_pending_src', {}).pop(os.path.abspath(p), None)
        if src: self._archive_source(src, say, new_base=os.path.splitext(base)[0])
        if name is None:
            self._no_cache = True   # engines found nothing: retry next run

    def handle_excel(self, p, say):
        if not os.path.isfile(p): return
        base = os.path.basename(p)
        if base.lower().startswith('summary'): return
        bl = base.lower()
        if not (bl.startswith(('book', 'untitled', 'sheet', 'export', 'query', 'results', 'data'))
                or bl.endswith('copy') or ' copy ' in bl or re.search(r'copy\s*\d*$', bl)):
            return
        self._rename(p, "Summary.xlsx", say, 'excel')
        self._compact_numbers(os.path.dirname(p), say)

    def route(self, p, say):
        # DOWNLOAD-STABILITY-GATE v39
        try:
            _bn = os.path.basename(p).lower()
            if _bn.endswith(('.crdownload', '.part', '.tmp', '.tmp.html', '.download')) or _bn.startswith('unconfirmed'):
                return
            _st = os.stat(p)
            if _st.st_size == 0:
                return
            if time.time() - _st.st_mtime < 3.0:
                time.sleep(2.0)
                _s2 = os.stat(p)
                if _s2.st_size != _st.st_size or _s2.st_mtime != _st.st_mtime:
                    return
        except Exception:
            return
        try: self.heat = getattr(self, 'heat', {}); self.heat[self.position_folder_for(p)] = time.time()
        except Exception: pass
        p = os.path.abspath(p)
        if os.path.basename(os.path.dirname(p)).lower() in ('converted doc files', 'converted files', 'duplicates', 'previous versions'):
            return
        if not hasattr(self, 'journal'): self._jload()
        jk = self._jkey(p)
        self._skip_tags = bool(jk and self.journal.get(p) == jk)
        self._no_cache = False
        acted = []
        def wsay(m):
            acted.append(1)
            say(m)
        if p.lower().endswith('.eml'):
            pdf = self.handle_convert(p, wsay)
            if pdf: self.handle_pdf(pdf, wsay)
            if acted and not getattr(self, 'scanning', False):
                say("   👀 back to watching…")
            return
        with self.lock:
            if p in self.busy: return
            self.busy.add(p)
        try:
            self._route(p, wsay)
        finally:
            with self.lock:
                self.busy.discard(p)
            if jk and not getattr(self, '_no_cache', False):
                self.journal[p] = jk
                self._jdirty = True
            if acted and not getattr(self, 'scanning', False):
                say("   👀 back to watching…")
    def _pend(self, p, say=print):
        if not hasattr(self, '_pending'): self._pending = {}
        self._pending[p] = time.time()
    def _drain_pending(self, say=print):
        if not hasattr(self, '_pending'): return
        now = time.time()
        for p in [p for p, t in list(self._pending.items()) if now - t > 3 and os.path.exists(p) and not _settling(p)]:
            self._pending.pop(p, None)
            self._route(p, say, skip_tags=False)

    def _tag_poll(self):
        import zlib as _z
        if not hasattr(self, '_tagcrc'): self._tagcrc = {}
        if not hasattr(self, '_tagct'): self._tagct = {}
        if not hasattr(self, '_tag_kind'): self._tag_kind = {}
        if not getattr(self, '_bp_loaded', False):  # BASELINE-PERSIST v81.29: remember tags across restarts
            self._bp_loaded = True
            try:
                _bl = json.load(open(os.path.join(BASE_DIR, 'tag_baseline.json')))
                for _p, _v in _bl.items():
                    self._tagcrc[_p] = _v[0]; self._tagct[_p] = _v[1]; self._tagsets[_p] = _v[2]
                if _bl: print(f'🧠 tag baseline restored: {len(_bl)} files remembered across restart', flush=True)
            except Exception:
                pass
        if not hasattr(self, '_tagsets'): self._tagsets = {}
        self._added_tags = {}
        now = time.time()
        gap = (now - getattr(self, '_last_poll_ts', 0)) > 300
        self._last_poll_ts = now
        changed = []
        for dp, dn, fn in os.walk(self.root):
            dn[:] = [x for x in dn if not x.startswith('.')]
            for f in fn:
                if not f.lower().endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue
                fp = os.path.join(dp, f)
                try: st = os.stat(fp).st_ctime  # CTIME-EYE v81.20: tag writes bump ctime even when the set returns to baseline
                except OSError: st = 0
                tg = _xattr_raw(fp)
                c = _z.crc32(tg)
                oldc = self._tagcrc.get(fp); oldt = self._tagct.get(fp)
                self._tagcrc[fp] = c; self._tagct[fp] = st
                prev = self._tagsets.get(fp)
                if oldc is None and oldt is None:
                    self._tagsets[fp] = [t for t in (_tags_of_fast(fp) or [])]
                elif oldc != c or oldt != st:
                    changed.append(fp)
                    self._tag_kind[fp] = 'set' if oldc != c else 'ctime'  # KIND v81.26
                    cur = [t for t in (_tags_of_fast(fp) or [])]
                    add = list(cur) if cur else []  # RETOUCH v81.19 + EVERY-TAG-EVENT v81.30: any observed tag/ctime change drafts every tag currently on the file
                    if add: self._added_tags[fp] = add
                    self._tagsets[fp] = cur
        if len(self._tagcrc) > 20000: self._tagcrc = {}
        if changed: print(f'🩺 poll changed={len(changed)} added={len(getattr(self, chr(95)+chr(97)+chr(100)+chr(100)+chr(101)+chr(100)+chr(95)+chr(116)+chr(97)+chr(103)+chr(115), {}))}', flush=True)  # PULSE-WITNESS v81.6
        self._bp_n = getattr(self, '_bp_n', 0) + 1
        if self._bp_n % 15 == 1:
            try:
                json.dump({p: [self._tagcrc.get(p), self._tagct.get(p), self._tagsets.get(p)] for p in self._tagcrc}, open(os.path.join(BASE_DIR, 'tag_baseline.json'), 'w'))
            except Exception:
                pass
        return changed

    def _snapshot(self, say=print):  # SNAPSHOT v69
        import subprocess, datetime, glob
        ic = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs')
        if not os.path.isdir(ic): return
        now = datetime.date.today()
        mind = os.path.join(ic, f'cv-memory-week-{now.isocalendar()[0]}-{now.isocalendar()[1]}.tgz')
        if now.weekday() == 6 and not os.path.exists(mind):
            subprocess.run(['tar', '-czf', mind, '--exclude=wa_profile', '--exclude=__pycache__', '--exclude=download_debris', '--exclude=cv_env', '--exclude=archive', '-C', os.path.expanduser('~'), 'CV_Tool', '-C', os.path.join(self.root), 'stage_log.json'], capture_output=True)
            say(f'☁️ weekly mind snapshot: {os.path.basename(mind)}')
        tree = os.path.join(ic, f'cv-tree-{now.strftime("%Y-%m")}.tgz')
        if now.day == 1 and not os.path.exists(tree):
            subprocess.run(['tar', '-czf', tree, '-C', os.path.dirname(self.root), os.path.basename(self.root)], capture_output=True)
            say(f'☁️ monthly tree snapshot: {os.path.basename(tree)}')
        for pat in ('cv-memory-week-*.tgz', 'cv-tree-*.tgz'):
            old = sorted(glob.glob(os.path.join(ic, pat)))[:-4]
            for o in old:
                try: os.remove(o)
                except Exception: pass

    def _summary_xlsx(self, p, say=print):  # SUMMARY-CANON v71
        try:
            b = os.path.basename(p).lower()
            if not b.endswith('.xlsx') or b.startswith('~$'): return p
            import re as _re
            if _re.match(r'summary(_\d+)?\.xlsx$', b): return p
            if _settling(p): return p
            import openpyxl
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
            ws = wb.active
            hdr = ' | '.join(str(c.value or '').strip() for c in next(ws.iter_rows(min_row=1, max_row=1)))
            wb.close()
            if 'Candidate Name' not in hdr or 'Position' not in hdr: return p
            d = os.path.dirname(p); n = 0
            while True:
                tgt = os.path.join(d, 'Summary.xlsx' if n == 0 else f'Summary_{n}.xlsx')
                if not os.path.exists(tgt): break
                n += 1
                if n > 50: return p
            os.rename(p, tgt); say(f'📊 [summary] {os.path.basename(p)} -> {os.path.basename(tgt)}')
            return tgt
        except Exception:
            return p

    def _ad_enabled(self):  # AUTODRAFT v81
        try: st = open(os.path.join(BASE_DIR, 'autodraft.flag')).read().strip()
        except Exception: st = 'auto'
        if st == 'off': return False
        if st in ('on', 'dry'): return True
        try:
            import subprocess
            return bool(subprocess.run(['pgrep', '-f', 'briefing.py chat'], capture_output=True).stdout.strip())
        except Exception: return False
    def _phone_for(self, phs):
        if not phs: return None
        nb = _names_by_phone()
        for d in phs:
            if d in nb: return d
        try: conv = json.load(open(os.path.join(BASE_DIR, 'conversations.json')))
        except Exception: conv = {}
        for d in phs:
            if d in conv: return d
        return phs[0]
    def _ad_fidget(self):  # FIDGET v81.27: testing switch - filesystem fidgeting re-drafts on demand
        try: return open(os.path.join(BASE_DIR, 'fidget.flag')).read().strip() == 'on'
        except Exception: return False

    def _ad_claim(self):  # SINGLE-FLIGHT v81.35: one release per state change; two tick callers, one queue
        now = time.time()
        if now - getattr(self, '_ad_last_release', 0) < 8: return False
        self._ad_last_release = now
        return True

    def _rename_clean(self, say=print):  # DASH-CLEAN v81.48: download scars are not part of a person's name
        n = 0
        for dp, dn, fn in os.walk(self.root):
            dn[:] = [x for x in dn if not x.startswith('.')]
            for f in fn:
                if not f.lower().endswith(('.pdf', '.doc', '.docx')): continue
                stem, ext = os.path.splitext(f)
                if '---' not in stem: continue
                clean = re.sub(r'\s*-{3,}\s*', ' ', stem).strip()
                clean = re.sub(r'\s{2,}', ' ', clean)
                if clean.replace('.', '').replace(' ', '').isupper(): clean = clean.title()
                if not clean or clean == stem: continue
                srcp = os.path.join(dp, f); dst = os.path.join(dp, clean + ext)
                if os.path.exists(dst): continue
                try:
                    os.rename(srcp, dst); n += 1
                    say(f'✏️ [rename-clean] {f} -> {clean + ext}')
                except Exception:
                    pass
        return n

    def _ad_busy(self):  # SEND-AWARE v81.24: the queue advances on your actual send
        try: st = json.load(open(os.path.join(BASE_DIR, 'ad_state.json')))
        except Exception: return getattr(self, '_ad_pending', 0) > time.time()
        if getattr(self, '_ad_held', 0) > time.time(): return True  # HELD v81.35: one fire per tick, decided synchronously
        if st.get('state') == 'waiting':  # PID-ALIVE v81.34: a killed watcher is not a busy window
            try: os.kill(int(st.get('pid', 0)), 0)
            except Exception: return False
            return time.time() - st.get('ts', 0) < 1900
        return False

    def _ad_fire(self, d, txt, v, nm, say, fp='', tg=''):  # AD-FIRE v81.5 (subprocess: playwright needs a main thread)
        import subprocess, sys
        self._ad_pending = time.time() + 75
        say(f'📝 autodraft: {v} -> +{d} ({nm})')
        try:
            tf = os.path.join(BASE_DIR, 'ad_draft.txt')
            open(tf, 'w').write(txt)
            lf = open(os.path.join(BASE_DIR, 'ad_fire.log'), 'a')
            try: json.dump({'fp': fp, 'tag': tg, 'phone': d, 'voice': v}, open(os.path.join(BASE_DIR, 'ad_meta.json'), 'w'))
            except Exception: pass
            self._ad_held = time.time() + 90  # HELD v81.35: mark the window held before the child can speak
            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'ad_wait.py'), d, tf], cwd=BASE_DIR, stdout=lf, stderr=subprocess.STDOUT)  # WA-WAIT v81.24: the window lives until your send empties the field
        except Exception as e:
            say(f'⚠️ autodraft fire failed: {e}')

    def _ad_text(self, fp, v, nm):  # FRESH-TEXT v81.26: queued drafts rebuild wording at fire time
        try:
            rel = os.path.relpath(os.path.dirname(fp), self.root).split(os.sep) if fp else []
            if len(rel) < 2: return None
            client, posraw = rel[0], rel[1]
            pos = posraw.split('||')[0].strip().replace('_', ' ')
            loc = posraw.split('||')[1].strip() if '||' in posraw else ''
            t = open(os.path.join(BASE_DIR, 'templates', f'voice_{v}.txt')).read()
            return t.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc)
        except Exception:
            return None

    def _draft_one(self, fp, tg, v, mode, say, kind='set'):
        try:
            if not os.path.exists(fp):
                hit = None
                for dp, dn, fn in os.walk(self.root):
                    dn[:] = [x for x in dn if not x.startswith('.')]
                    if os.path.basename(fp) in fn: hit = os.path.join(dp, os.path.basename(fp)); break
                if not hit: say(f'⏭️ autodraft skip (gone): {os.path.basename(fp)}'); return
                fp = hit
            if _settling(fp): say(f'⏭️ autodraft skip (settling): {os.path.basename(fp)}'); return
            rel = os.path.relpath(os.path.dirname(fp), self.root).split(os.sep)
            if len(rel) < 2: say(f'⏭️ autodraft skip (no position folder): {os.path.basename(fp)}'); return
            client, posraw = rel[0], rel[1]
            pos = posraw.split('||')[0].strip().replace('_', ' ')
            loc = posraw.split('||')[1].strip() if '||' in posraw else ''
            try:
                phs = phones_of(fp) or []
            except Exception: phs = []
            d = self._phone_for(phs)
            if not d: say(f'⏭️ autodraft skip (no phone): {os.path.basename(fp)}'); return
            lp = os.path.join(BASE_DIR, 'autodraft_log.json')
            try: lg = json.load(open(lp))
            except Exception: lg = {}
            k = f'{fp}|{tg}'  # 60s debounce per file+tag, replaces 24h cooldown
            if False and time.time() - lg.get(k, 0) < 60: return  # NEUTER-DEBOUNCE v81.30 (user spec: every tag action is a new event)
            if False and kind == 'ctime': pass  # NEUTER-DONEMARK v81.30 (every tag action is a new event)
            if kind == 'ctime' and not self._ad_fidget(): say(f'⏭️ autodraft: {os.path.basename(fp)} +{tg} ctime-only touch (Finder preview/index), not a tag action - fidget.flag on drafts these'); return  # KIND-RESPECT v81.44
            nm = _names_by_phone().get(d) or os.path.splitext(os.path.basename(fp))[0]
            try: txt = open(os.path.join(BASE_DIR, 'templates', f'voice_{v}.txt')).read()
            except Exception: say(f'⚠️ autodraft: missing template voice_{v}'); return
            txt = txt.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc)
            lg[k] = time.time(); json.dump(lg, open(lp, 'w'), indent=1)
            if mode == 'dry':
                say(f'📝 [dry] {v} -> +{d} ({nm}): {txt[:110]}…'); return
            if self._ad_busy():
                qp = os.path.join(BASE_DIR, 'autodraft_queue.json')
                try: q = json.load(open(qp))
                except Exception: q = []
                q = [x for x in q if time.time() - x.get('at', 0) < 7200]
                if not any(_x.get('phone') == d and _x.get('who') == nm for _x in q):  # DEDUPE v81.44: one queued draft per candidate
                    q.append({'phone': d, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v, 'fp': fp, 'tag': tg})
                json.dump(q, open(qp, 'w'), indent=1)
                say(f'📝 queued autodraft: {v} -> {nm} (+{d}) - slides into the open window the moment you send'); return
            self._ad_fire(d, txt, v, nm, say, fp, tg)
            for _d2 in phs:  # MULTI-NUM v81.19: every number in the CV gets its own draft
                if _d2 == d: continue
                try: q2 = json.load(open(os.path.join(BASE_DIR, 'autodraft_queue.json')))
                except Exception: q2 = []
                q2 = [x for x in q2 if time.time() - x.get('at', 0) < 7200]
                q2.append({'phone': _d2, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v, 'fp': fp, 'tag': tg})
                json.dump(q2, open(os.path.join(BASE_DIR, 'autodraft_queue.json'), 'w'), indent=1)
                say(f'📝 queued autodraft (extra number +{_d2}): {nm}')
        except Exception as e:
            say(f'⚠️ autodraft error: {e}')
    def _autodraft_tick(self, say=print):
        try:
            try: st = open(os.path.join(BASE_DIR, 'autodraft.flag')).read().strip() or 'auto'
            except Exception: st = 'auto'
            if not self._ad_enabled():
                if getattr(self, '_added_tags', None):
                    n = sum(len(v) for v in self._added_tags.values())
                    if n: say(f'🔕 autodraft off (flag={st}) - {n} tag-add(s) ignored')  # AD-VISIBILITY v81.1
                    self._added_tags = {}
                return
            mode = 'auto'
            try: mode = open(os.path.join(BASE_DIR, 'autodraft.flag')).read().strip() or 'auto'
            except Exception: mode = 'auto'
            try: stt = json.load(open(os.path.join(BASE_DIR, 'ad_state.json')))
            except Exception: stt = {}
            if stt.get('state') in ('sent', 'retired') and stt.get('meta') and getattr(self, '_ad_done_seen', 0) != stt.get('ts'):
                self._ad_done_seen = stt.get('ts')
                m = stt['meta']
                lp2 = os.path.join(BASE_DIR, 'autodraft_log.json')
                try: lg2 = json.load(open(lp2))
                except Exception: lg2 = {}
                lg2[str(m.get('fp')) + '|' + str(m.get('tag'))] = time.time()
                json.dump(lg2, open(lp2, 'w'), indent=1)
                say('📬 draft round closed (' + str(stt.get('state')) + ') for ' + str(m.get('tag')) + ' - noted done this round')  # DONE-MARK v81.26
            qp = os.path.join(BASE_DIR, 'autodraft_queue.json')
            q = []  # Q-INIT v81.40: the witness may read the queue even when the release gate skips
            try:
                _q0 = json.load(open(qp)); _q1 = [x for x in _q0 if time.time() - x.get('at', 0) < 900]
                if len(_q1) != len(_q0): say(f'🗑 pruned {len(_q0) - len(_q1)} stale queued draft(s) older than 15 min')
                json.dump(_q1, open(qp, 'w'), indent=1)  # STALE-JOB-PRUNE v81.45: nameless old intent expires
            except Exception:
                pass
            if not self._ad_busy() and self._ad_claim():
                try: q = json.load(open(qp))
                except Exception: q = []
                q = [x for x in q if time.time() - x.get('at', 0) < 7200]
                if q:
                    it = q.pop(0); json.dump(q, open(qp, 'w'), indent=1)
                    say(f"▶️ window free - releasing queued draft for +{it.get('phone')} ({it.get('who')})")  # RELEASE-VOICE v81.32
                    self._ad_fire(it['phone'], self._ad_text(it.get('fp',''), it['voice'], it['who']) or it.get('text',''), it['voice'], it['who'], say, it.get('fp',''), it.get('tag',''))  # FRESH-TEXT v81.26
            added, self._added_tags = getattr(self, '_added_tags', {}), {}
            try: vm = json.load(open(os.path.join(BASE_DIR, 'tag_voices.json')))
            except Exception: return
            if not hasattr(self, '_ad_lastlog'): self._ad_lastlog = 0
            if added or q or time.time() - self._ad_lastlog > 300:
                self._ad_lastlog = time.time()
                say(f'🩺 autodraft tick: enabled={self._ad_enabled()} mode={mode} adds={len(added)} queue={len(q)}')  # TICK-WITNESS v81.6
            for fp, tags in added.items():
                for tg in tags:
                    v = vm.get(tg) or vm.get(tg.replace(chr(8211), '-'))
                    say(f'🏷️ tag-add: {os.path.basename(fp)} +{tg}')  # TAGADD-LOG v81.5
                    if v: self._draft_one(fp, tg, v, mode, say, getattr(self, '_tag_kind', {}).get(fp, 'set'))
        except Exception as e:
            say(f'⚠️ autodraft tick: {e}')

    def _heal(self, say=print):
        if not hasattr(self, '_pending'): self._pending = {}
        if not hasattr(self, '_heal_done'): self._heal_done = {}
        now = time.time()
        for p in [p for p, t in list(self._pending.items()) if now - t > 20 and os.path.exists(p) and not _settling(p)]:
            self._pending.pop(p, None)
            self._route(p, say, skip_tags=False)
        deb = os.path.join(BASE_DIR, 'download_debris')
        for dp, dn, fn in os.walk(self.root):
            dn[:] = [d for d in dn if not d.startswith('.')]
            for f in fn:
                fp = os.path.join(dp, f); bl = f.lower()
                try: st = os.stat(fp)
                except OSError: continue
                if bl.endswith(SETTLE_EXTS) and now - st.st_mtime > 6 * 3600:
                    os.makedirs(deb, exist_ok=True)
                    try:
                        os.rename(fp, os.path.join(deb, f)); say(f'🧹 debris archived: {f}')
                    except Exception: pass
                    continue
                if bl.endswith(SETTLE_EXTS): continue
                if '.' in bl and not bl.endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue
                if _settling(fp): continue
                key = f'{fp}|{st.st_mtime_ns}|{st.st_size}'
                prev = self._heal_done.get(f)
                if prev and prev[0] == key and now - prev[1] < 30: continue  # HEAL-RETRY v65
                self._heal_done[f] = (key, now)
                try: self.rc.pop(os.stat(fp).st_ino, None)  # RC-FRESH v66
                except Exception: pass
                if '.' not in bl:  # HEAL-SNIFF v72
                    _se = _sniff_ext(fp)
                    if _se:
                        _nb = fp + _se; _n2 = 1
                        while os.path.exists(_nb): _nb = f'{fp}_{_n2}{_se}'; _n2 += 1
                        try:
                            os.rename(fp, _nb); say(f'🧩 [suffix] {os.path.basename(fp)} -> {os.path.basename(_nb)}'); fp = _nb; bl = os.path.basename(_nb).lower()
                        except Exception: continue
                self._route(fp, say, skip_tags=False)

    def _route(self, p, say, skip_tags=None):
        sk = skip_tags if skip_tags is not None else getattr(self, '_skip_tags', False)  # SKIP-FIX v74
        if p.lower().endswith('.tmp.html'):
            try:
                if time.time() - os.path.getmtime(p) > 600:
                    os.remove(p)
                    say(f"\n🧹 [clean] removed stale temp: {os.path.basename(p)}")
            except Exception:
                pass
            return
        if _settling(p): self._pend(p, say); return  # ROUTE-GATE v60
        ext = os.path.splitext(p)[1].lower()
        if ext not in ('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx'):  # SNIFF-EXT v70
            _se = _sniff_ext(p)
            if _se:
                _d = os.path.dirname(p); _b = os.path.splitext(os.path.basename(p))[0] or 'untitled'
                _c = os.path.join(_d, _b + _se); _n = 1
                while os.path.exists(_c): _c = os.path.join(_d, f'{_b}_{_n}{_se}'); _n += 1
                try:
                    os.rename(p, _c); say(f'🧩 [suffix] {os.path.basename(p)} -> {os.path.basename(_c)}'); p = _c; ext = _se
                except Exception: pass
        if ext in ('.doc', '.docx', '.msg'):
            pdf = self.handle_convert(p, say)
            if pdf and os.path.exists(pdf):
                self.handle_pdf(pdf, say)
                if not getattr(self, '_skip_tags', False): self.handle_tags(pdf, say)
        elif ext == '.pdf':
            p = self.normalize_suffix(p, say)
            _ino = None  # INODE-RELINK v71
            try: _ino = os.stat(p).st_ino
            except Exception: pass
            if _ino is not None and not os.path.exists(p):
                for _f in os.listdir(os.path.dirname(p)):
                    _c = os.path.join(os.path.dirname(p), _f)
                    try:
                        if os.stat(_c).st_ino == _ino: p = _c; break
                    except Exception: pass
            self.handle_pdf(p, say)
            if not sk: self.handle_tags(p, say)
            self._compact_numbers(os.path.dirname(p), say)
        elif ext == '.xlsx':
            p = self._summary_xlsx(p, say)  # SUMMARY-CALL v71
            self.handle_excel(p, say)
            if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)
            self._compact_numbers(os.path.dirname(p), say)

    def _folder_for_tag(self, base, tag):
        def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')
        try:
            for d in os.listdir(base):
                if os.path.isdir(os.path.join(base, d)) and _n(d) == _n(tag):
                    return os.path.join(base, d)
        except Exception:
            pass
        return os.path.join(base, tag)

    def handle_tags(self, p, say):
        if _settling(p): return  # TAGS-GATE v60
        T = _tags_of_fast(p) or get_tags(p) or []  # TAG-TRUTH v75: read, assume nothing
        for t in T:
            nm = re.sub(r'[/\\:]', '-', (t or '').split(chr(10))[0].strip())
            if not nm or nm in ('Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Gray', 'Grey'): continue
            d0 = os.path.dirname(p)
            if os.path.basename(d0) == nm: return  # HOME v78
            base = d0 if len(os.path.relpath(d0, self.root).split(os.sep)) <= 2 else os.path.dirname(d0)
            tgt = os.path.join(base, nm)
            os.makedirs(tgt, exist_ok=True)
            dst = os.path.join(tgt, os.path.basename(p)); c = 1
            b2, e2 = os.path.splitext(os.path.basename(p))
            while os.path.exists(dst): dst = os.path.join(tgt, f'{b2}_{c}{e2}'); c += 1
            if _settling(p): return
            try:
                os.rename(p, dst); say(f'📁 [move] {os.path.basename(p)} -> {nm}/'); return
            except Exception: return
        return  # TAG-TRUTH-AUTHORITATIVE v78
        if len(os.path.relpath(os.path.dirname(p), self.root).split(os.sep)) < 2:  # CLIENT-ROOT v73
            for t in ((_tags_of_fast(p) or get_tags(p)) or []):
                tt = t.replace(chr(8211), '-')
                if tt in TAG_NAMES or t in TAG_NAMES:
                    nm = re.sub(r'[/\\:]', '-', tt)
                    tgt = os.path.join(os.path.dirname(p), nm)
                    os.makedirs(tgt, exist_ok=True)
                    dst = os.path.join(tgt, os.path.basename(p)); c = 1
                    b2, e2 = os.path.splitext(os.path.basename(p))
                    while os.path.exists(dst): dst = os.path.join(tgt, f'{b2}_{c}{e2}'); c += 1
                    if _settling(p): return
                    try:
                        os.rename(p, dst); say(f'📁 [move] {os.path.basename(p)} -> {nm}/ (client root)')
                    except Exception: pass
                    return
        if len(os.path.relpath(os.path.dirname(p), self.root).split(os.sep)) < 2: return
        T = _tags_of_fast(p) or get_tags(p)
        if len(os.path.relpath(os.path.dirname(p), self.root).split(os.sep)) < 2:  # CLIENT-ROOT v72
            for t in (T or []):
                tt = t.replace(chr(8211), '-')
                if tt in TAG_NAMES or t in TAG_NAMES:
                    nm = re.sub(r'[/\\:]', '-', tt)
                    tgt = os.path.join(os.path.dirname(p), nm)
                    os.makedirs(tgt, exist_ok=True)
                    dst = os.path.join(tgt, os.path.basename(p)); c = 1
                    b2, e2 = os.path.splitext(os.path.basename(p))
                    while os.path.exists(dst): dst = os.path.join(tgt, f'{b2}_{c}{e2}'); c += 1
                    if _settling(p): return
                    try:
                        os.rename(p, dst); say(f'📁 [move] {os.path.basename(p)} -> {nm}/ (client root)')
                    except Exception: pass
                    return
        named = [t for t in T if t in TAG_NAMES or t.replace(chr(8211), "-") in TAG_NAMES]
        if not named: return
        tag = named[0]
        safe_tag = re.sub(r'[\\/:*?"<>|]', '', tag).strip()
        if not safe_tag: return
        target_folder = self._folder_for_tag(self.position_folder_for(p), safe_tag)
        if os.path.abspath(os.path.dirname(p)) == os.path.abspath(target_folder): return
        os.makedirs(target_folder, exist_ok=True)
        dst = os.path.join(target_folder, os.path.basename(p))
        if os.path.exists(dst):
            b, e = os.path.splitext(os.path.basename(p)); c = 1
            while os.path.exists(dst): dst = os.path.join(target_folder, f"{b}_{c}{e}"); c += 1
        os.rename(p, dst)
        with self.lock: self.stats['moved'] += 1
        say(f"\U0001f4c1 [move] {os.path.basename(p)} -> {safe_tag}/")
        return dst
    def sweep_dirs(self, n):
        now = time.time()
        dirs = []
        f = None
        try:
            import briefing as _b
            fz = _b._read_focus()
            f = fz['path'] if fz else None
        except Exception:
            f = None
        if f and f.startswith(self.root): dirs.append(f)
        for pp, tt in list(getattr(self, 'heat', {}).items()):
            if now - tt < 1800 and pp not in dirs and pp.startswith(self.root): dirs.append(pp)
        if n % 3 == 0:
            for pp in list(dirs):
                cc = os.path.dirname(pp)
                if cc not in dirs and cc.startswith(self.root): dirs.append(cc)
        if n % 9 == 0 or not dirs: dirs = [self.root]
        return dirs

    def _reconcile_tags(self, say, dirs=None):
        def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')
        known = {_n(t): t for t in TAG_NAMES}
        for _d0 in (dirs or [self.root]):
            for dp, dn, fn in os.walk(_d0):
                if len(os.path.relpath(dp, self.root).split(os.sep)) < 2: continue
                dn[:] = [x for x in dn if not x.startswith(".")]
                for f in fn:
                    if not f.lower().endswith(".pdf"): continue
                    fp = os.path.join(dp, f)
                    T = _tags_of_fast(fp) or get_tags(fp)
                    _here = os.path.basename(os.path.dirname(fp))  # ALREADY-FILED v77
                    if _here and _here in [re.sub(r'[/\\:]', '-', (x or '').split(chr(10))[0].strip()) for x in (T or [])]: continue
                    tag = None
                    for t in T:
                        if _n(t) in known: tag = known[_n(t)]; break
                    if not tag: continue
                    tgt = self._folder_for_tag(self.position_folder_for(fp), tag)
                    if os.path.abspath(os.path.dirname(fp)) == os.path.abspath(tgt): continue
                    os.makedirs(tgt, exist_ok=True)
                    dst = os.path.join(tgt, f)
                    if os.path.exists(dst):
                        b2, e2 = os.path.splitext(f); c2 = 1
                        while os.path.exists(dst): dst = os.path.join(tgt, f"{b2}_{c2}{e2}"); c2 += 1
                    if _settling(fp): continue  # RECONCILE-GATE v60
                    self.handle_pdf(fp, say)  # RENAME-FIRST v65
                    if not os.path.exists(fp): continue
                    os.rename(fp, dst)
                    with self.lock: self.stats['moved'] += 1
                    say(f"\U0001f4c1 [reconcile] {f} -> {tag}/")
                    try:
                        _g = locals()
                        _pp = _g.get('p') or _g.get('fp') or _g.get('src')
                        _tt = _g.get('tag') or _g.get('tg') or _g.get('stage')
                        if _pp and _tt:
                            self.slog.observe(os.path.splitext(os.path.basename(_pp))[0], _tt, os.path.relpath(self.position_folder_for(_pp), self.root))
                    except Exception:
                        pass

def main():
    print(f"🤖✨ {VERSION} · git {GIT_STAMP}")
    if len(sys.argv) > 1:
        root = os.path.normpath(os.path.expanduser(sys.argv[1]))
    else:
        if INTERACTIVE:  # REPL-GATE v81.12: only a real terminal gets the REPL; a log-file stdout walks to the watcher
            print("\nDRAG & DROP your working folder, then press Return:")
            root = input("> ")
        else:
            root = sys.stdin.readline()
        root = os.path.normpath(os.path.expanduser(root.strip().strip('"').strip("'").replace('\\', '')))
    if not os.path.isdir(root):
        print("Error: folder does not exist."); sys.exit(1)
        try:
            with open(os.path.expanduser('~/.cvtool_last_butler_root'), 'w') as f: f.write(root)
        except Exception: pass

    import hashlib
    lock_path = os.path.join(BASE_DIR, "butler_" + hashlib.md5(root.encode()).hexdigest()[:8] + ".lock")
    def _alive(lp):
        try:
            with open(lp) as f: pid = int(f.read().split('|')[0].strip())
            os.kill(pid, 0); return pid
        except Exception: return None
    _lp = _alive(lock_path)
    if _lp and _lp != os.getpid():
        print("⚠️ Another butler is already watching this folder."); sys.exit(1)
    for fn in os.listdir(BASE_DIR):
        if not (fn.startswith('butler_') and fn.endswith('.lock')): continue
        lp = os.path.join(BASE_DIR, fn)
        if lp == lock_path or not _alive(lp): continue
        try: other = open(lp).read().split('|', 1)[1].strip()
        except Exception: continue
        a, b = os.path.abspath(root), os.path.abspath(other)
        if a != b and (a.startswith(b + os.sep) or b.startswith(a + os.sep)):
            print(f"⚠️ A butler is already watching an overlapping folder: {other}")
            print("   Run butler on ONE level only (parent OR children), not both.")
            sys.exit(1)
    for _fn in os.listdir(os.path.dirname(lock_path)):
        if not (_fn.startswith('butler_') and _fn.endswith('.lock')): continue
        _lp = os.path.join(os.path.dirname(lock_path), _fn)
        if _lp == lock_path: continue
        try:
            _pid, _rt = open(_lp).read().strip().split('|', 1)
        except Exception:
            continue
        if not _alive(_lp): continue
        _a = root.rstrip('/') + '/'; _b = _rt.rstrip('/') + '/'
        if _rt != root and (_a.startswith(_b) or _b.startswith(_a)):
            print(f"⛔ refused: live butler {_pid} already covers {_rt} (one writer per tree) - use chat/CLI one-shots, not a second console")
            sys.exit(0)
    with open(lock_path, "w") as f: f.write(f"{os.getpid()}|{root}")

    ensure_ocr()
    global LLM_MODEL
    LLM_MODEL = get_model()
    B = Butler(root)
    B._jload()
    B.scanning = True
    # fresh-eyes purge: reset convert fail-counters each run
    _d = getattr(B, 'conv_state', None)
    if isinstance(_d, dict):
        setattr(B, 'conv_state', {k: v for k, v in _d.items() if not k.startswith('fail:')})
    B._save()
    B._save()
    print(f"🔧 convert engines: {', '.join(n for n, _ in B.engines) or 'NONE'} · 🤖 AI: {LLM_MODEL or 'OFFLINE'}")
    briefing.print_briefing(root)

    ex = ThreadPoolExecutor(max_workers=4)
    def _pulse_loop():  # PULSE-THREAD v81.13: the pulse lives in no branch's custody
        import time as _t  # PULSE-CLOCK v81.14: the thread owns its clock; no enclosing cell may starve it
        print('🩺 pulse thread armed', flush=True)
        while True:
            try:
                if time.time() - getattr(B, '_last_poll', 0) > 4:
                    B._last_poll = time.time()
                    for _cp in B._tag_poll(): ex.submit(work, _cp)
                    B._autodraft_tick()
                if time.time() - getattr(B, '_last_hb_t', 0) > 120:
                    B._last_hb_t = time.time()
                    try: B._heal(print)
                    except Exception: pass
                if time.time() - getattr(B, '_last_snap_t', 0) > 3600:
                    B._last_snap_t = time.time()
                    try: B._snapshot(print)
                    except Exception: pass
            except Exception as e:
                print(f'⚠️ pulse thread: {e}', flush=True)
            if time.time() - getattr(B, '_warm_keep', 0) > 60:  # WARM-KEEPALIVE v81.44: the keeper is respawned unless you closed it yourself
                B._warm_keep = time.time()
                try:
                    _cl = os.path.join(BASE_DIR, 'wa_warm_closed.ts')
                    _rc = os.path.exists(_cl) and time.time() - os.stat(_cl).st_mtime < 600
                    _sa = False
                    try:
                        import socket as _sk; _sx = _sk.create_connection(('127.0.0.1', 9222), timeout=2); _sx.close(); _sa = True  # WARM-SUPERVISOR v81.45: the port, not the process, is the truth
                    except Exception:
                        _sa = False
                    _pa = os.system("pgrep -f 'wa_warm.py' >/dev/null 2>&1") == 0
                    if not _rc and not _sa and not _pa:
                        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'wa_warm.py'), 'ensure'], cwd=BASE_DIR, stdout=open(os.path.join(BASE_DIR, 'wa_warm.log'), 'a'), stderr=subprocess.STDOUT, start_new_session=True)
                        print('\U0001f525 warm keepalive: relaunching wa_warm', flush=True)
                except Exception:
                    pass
            time.sleep(2)
    import threading as _th

    dirty = set(); dlock = threading.Lock()
    class H(FileSystemEventHandler):
        def _add(self, p):
            with dlock: dirty.add(p)
        def on_created(self, e):
            if not e.is_directory: self._add(e.src_path)
        def on_modified(self, e):
            if not e.is_directory: self._add(e.src_path)
        def on_moved(self, e):
            if not e.is_directory:
                self._add(e.dest_path)
                if not e.dest_path.startswith(B.root):
                    B._check_siblings(os.path.dirname(e.src_path))
        def on_deleted(self, e):
            if not e.is_directory:
                B._check_siblings(os.path.dirname(e.src_path))
    obs = Observer(); obs.schedule(H(), path=root, recursive=True); obs.start()
    cleaner.clean_tree(root, print)   # startup tidy (Trash-only, two-observation rule)

    files = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for f in fn:
            if not f.startswith('.'): files.append(os.path.join(dp, f))

    prog = {'n': 0, 'lock': threading.Lock()}
    def work(p, total=0):
        if total:
            with prog['lock']:
                prog['n'] += 1
                print(f"🔎 {prog['n']}/{total} · {os.path.basename(p)}", flush=True)
        try:
            if not hasattr(B, 'journal'): B._jload()
            _jk = B._jkey(p)
            if _jk and B.journal.get(p) == _jk: return  # WORK-DOOR SKIP v63
        except Exception: pass
        try:
            B.route(p, print)
        except Exception as e:
            log.error(f"route error {p}: {e}")

    B.scan_idx = {str(i + 1): os.path.abspath(p) for i, p in enumerate(files)}
    B.scan_idx = {}
    B.scan_ino = {}
    for _i, _p in enumerate(files):
        B.scan_idx[str(_i+1)] = os.path.abspath(_p)
        try: B.scan_ino[str(_i+1)] = os.stat(_p).st_ino
        except OSError: pass
    B._save_idx()
    try:
        os.system("pkill -f 'ad_wait.py' 2>/dev/null; pgrep -f 'wa_warm.py' >/dev/null 2>&1 || pkill -f 'Google Chrome for Testing' 2>/dev/null")  # STALE-WINDOW-SWEEP v81.32: zombies die, owned warm browser lives # OWNER-AWARE v81.38
        try:
            json.dump({'state': 'retired', 'ts': time.time()}, open(os.path.join(BASE_DIR, 'ad_state.json'), 'w'))  # SWEEP-RESET v81.34
        except Exception:
            pass
            try:
                subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'wa_warm.py'), 'ensure'], cwd=BASE_DIR, stdout=open(os.path.join(BASE_DIR, 'wa_warm.log'), 'a'), stderr=subprocess.STDOUT, start_new_session=True)  # WA-WARM v81.37
            except Exception:
                pass
    except Exception:
        pass
    _BOOT_T = time.time()
    print(f"⏳ Scanning {len(files)} files… let it FINISH.")
    futs = [ex.submit(work, p, len(files)) for p in files]
    try:
        while True:
            _, nd = wait(futs, timeout=1)
            if not nd: break
    except KeyboardInterrupt:
        print("\n⛔ Stopped early — progress kept.")
        obs.stop(); sys.exit(0)
    self._rename_clean()
    print(f"\n✅ Scan complete · ⚙️ {B.stats['converted']} converted · ✏️ {B.stats['renamed']} renamed · 📦 {B.stats['moved']} moved")
    print(f"⏱ boot scan {time.time()-_BOOT_T:.1f}s · journal-skipped most of it")
    try:
        B._reconcile_tags(print)
        try:
            import fitrank; fitrank.tick(B)
            import ledger; ledger.tick(B)
        except Exception:
            pass
        B._compact_numbers(B.root, print)
    except Exception as _se:
        print('startup-reconcile error:', _se)
    B._save_idx()
    B.scanning = False
    print("👀 Watching silently… (Ctrl+C to quit)\n")
    def _console_start():
        try:
            tty = open('/dev/tty', 'r')
        except Exception:
            return
        import threading as _th
        def _console(tty):
            global INTERACTIVE
            while True:
                INTERACTIVE = True
                try:
                    raw = tty.readline().strip(); line = raw.lower()
                except Exception:
                    INTERACTIVE = False
                    return
                INTERACTIVE = False
                if not line: continue
                if line in ('chat', 'c'):
                    try:
                        lr = os.path.expanduser('~/.cvtool_last_root')
                        if not os.path.exists(lr):
                            with open(lr, 'w') as f: f.write(root)
                        import subprocess as _sp
                        _sp.run(['osascript', '-e', 'tell application "Terminal" to do script "cd ~/CV_Tool && cv_env/bin/python3 briefing.py chat"'], capture_output=True, timeout=15)
                        print("💬 chat opened in a new window - already synced to this folder")
                    except Exception as e:
                        print(f"⚠️ could not open chat: {e}")
                elif line in ('focus', 'f'):
                    import json as _j
                    _j.dump({'path': root, 'display': briefing.clean_pos(os.path.basename(root)),
                             'client': re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root))), 'also': []},
                            open(briefing.FOCUS_FILE, 'w'), indent=2)
                    print(f"🎯 focus pinned to this position: {os.path.basename(root)}")
                elif line.startswith('focus '):
                    briefing.do_focus(line[6:], briefing._company_root(root), print)
                elif line.startswith(('phonefix ', 'fixphone ')):
                    briefing.do_phonefix((raw if 'raw' in dir() else line).split(' ', 1)[1], root, print)
                elif line.startswith('learn '):
                    try:
                        k, v = line[6:].split('=', 1)
                        learn_name(k.strip(), v.strip())
                        print(f"🧠 learned: {k.strip()} -> {v.strip()} (applies to every future CV with that header)")
                    except Exception:
                        print("usage: learn <header text> = <Correct Name>")
                elif line.startswith('name '):
                    briefing.do_name(line[5:], root, print)
                elif line.startswith(('wa ', 'missed ', 'reject ', 'jd ', 'nudge ', 'touch ', 'text ')):
                    f = briefing._read_focus()
                    if not f or os.path.abspath(f.get('path', '')) != os.path.abspath(root):
                        json.dump({'path': root, 'display': briefing.clean_pos(os.path.basename(root)),
                                     'client': re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root))), 'also': []},
                                    open(briefing.FOCUS_FILE, 'w'), indent=2)
                        print(f"🎯 focus auto-set to this position: {os.path.basename(root)}")
                    def _ask(prompt):
                        global INTERACTIVE
                        print(prompt, end='', flush=True)
                        INTERACTIVE = True
                        try: return tty.readline().strip()
                        finally: INTERACTIVE = False
                    try:
                        if line.startswith('wa '): briefing.do_wa(raw[3:], root, print, ask=_ask)
                        elif line.startswith('missed '): briefing.do_missed(raw[7:], root, print, ask=_ask)
                        elif line.startswith('history '): briefing.do_history(raw[8:], root, print)
                        elif line.startswith('stale'): briefing.do_stale(raw[5:].strip(), root, print)
                        elif line.startswith('reject '): briefing.do_reject(raw[6:], root, print, ask=_ask)
                        elif line.startswith('jd '): briefing.do_send(raw[3:], root, ['jd shared'], print, ask=_ask)
                        elif line.startswith('nudge '): briefing.do_send(raw[6:], root, ['awaiting', 'confirmation'], print, ask=_ask)
                        elif line.startswith('touch '): briefing.do_send(raw[6:], root, ['keep', 'touch'], print, ask=_ask)
                        elif line.startswith('text '): briefing.do_text(raw[5:], root, print, ask=_ask)
                    except Exception as e:
                        print(f"️ {e}")
                elif line in ('brief', 'b'):
                    briefing.print_briefing(root, print)
                elif line in ('list', 'ls', 'who'):
                    briefing.do_list(root, print)
                elif line in ('status', 's'):
                    print(f"💓 ⚙️{B.stats['converted']} · ✏️{B.stats['renamed']} · 📦{B.stats['moved']}")
                elif line in ('restart', 'r'):
                    print('🔄 restarting on the same folder, same window…', flush=True)
                    time.sleep(0.3)
                    os.execv(sys.executable, [sys.executable, os.path.join(BASE_DIR, 'butler.py'), root])
                elif line in ('quit', 'stop', 'q'):
                    try: import wa; wa.close()
                    except Exception: pass
                    os._exit(0)
                else:
                    try: briefing.answer(root, raw, print)
                    except Exception as e: print(f"⚠️ {e}")
        _th.Thread(target=_console, args=(tty,), daemon=True).start()
        print("   💬 type here: chat · focus · learn · missed/wa/jd/nudge/touch/text <name or scan-#> · status · restart · stop")
    _th.Thread(target=_pulse_loop, daemon=True).start()  # PULSE-START-LATE v81.15: born after every name it closes over exists
    _console_start()

    last_full = time.time(); last_hb = time.time(); last_clean = time.time(); n = 0
    try:
        while True:
            import time as _t
            B._n = getattr(B, '_n', 0) + 1
            if B._n > 3 and (time.time() - getattr(B, '_last_sweep', 0)) < 120:
                with dlock:
                    _ip = list(dirty); dirty.clear()
                for p in _ip: ex.submit(work, p)
                try: B._drain_pending(print)
                except Exception: pass
                if getattr(B, '_jdirty', False):
                    B._jsave(); B._jdirty = False
                try:  # LOOP-ARMOUR v76
                    if time.time() - getattr(B, '_last_poll', 0) > 4:  # TAG-POLL v64
                        B._last_poll = time.time()
                        for _cp in B._tag_poll(): ex.submit(work, _cp)
                        B._autodraft_tick()
                        B._heal((lambda m: None) if INTERACTIVE else print)
                    open(os.path.join(BASE_DIR, 'butler_alive.stamp'), 'w').write(str(time.time()))
                except Exception as _e:
                    print(f'⚠️ pulse skipped: {_e}', flush=True)
                time.sleep(2); continue   # idle: events drained every tick
            B._last_sweep = time.time()
            if B._n == 4:
                print('😴 idle mode: event-driven now · safety sweep every 10 min')
            time.sleep(1)
            with dlock:
                paths = list(dirty); dirty.clear()
            for p in paths: ex.submit(work, p)
            try: B._drain_pending(print)  # DRAIN-PENDING v62
            except Exception: pass
            if time.time() - getattr(B, '_last_poll', 0) > 4:  # TAG-POLL v64
                B._last_poll = time.time()
                for _cp in B._tag_poll(): ex.submit(work, _cp)
                B._autodraft_tick()
                B._heal((lambda m: None) if INTERACTIVE else print)
            if time.time() - last_full > 20:
                last_full = time.time()
                for dp, dn, fn in os.walk(root):
                    dn[:] = [d for d in dn if not d.startswith('.')]
                    for f in fn:
                        if not f.startswith('.'): ex.submit(work, os.path.join(dp, f))
            if time.time() - last_clean > 86400:
                last_clean = time.time()
                cleaner.clean_tree(root, print)
            if time.time() - last_hb > 120:
                last_hb = time.time(); n += 1
                if not INTERACTIVE:
                    print(f"💓 sweep #{n} · quiet · ⚙️ {B.stats['converted']} · ✏️ {B.stats['renamed']} · 📦 {B.stats['moved']}")
                def hsay(m):
                    if INTERACTIVE: log.info(m)
                    else: print(m)
                try:
                    # LOG-TRIM v51
                    _lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'butler_live.log')
                    if os.path.exists(_lp) and os.path.getsize(_lp) > 5_000_000:
                        open(_lp, 'w').write(open(_lp, errors='ignore').read()[-500_000:])
                except Exception:
                    pass
                if _git_stamp() != GIT_STAMP:
                    print(f"⚠️ newer committed code exists (git {_git_stamp()}) - type  restart  to run the latest proven version")
                try:
                    for dp, dn, fn in os.walk(B.root):
                        dn[:] = [x for x in dn if not x.startswith(".")]
                        B._compact_numbers(dp, print)
                except Exception as _ce:
                    print(f"compact sweep error: {_ce}")
                try:
                    B._reconcile_tags(hsay, B.sweep_dirs(n))
                    try:
                        import fitrank; fitrank.tick(B)
                        import ledger; ledger.tick(B)
                        import cadence; cadence.process(B, hsay)
                        import sem; sem.tick(B)
                        B._heal(hsay)
                    except Exception:
                        pass
                except Exception as _re:
                    print('reconcile error:', _re)
    except KeyboardInterrupt:
        print("🛑 butler stopped - lock released. bye!", flush=True)
        obs.stop()
    finally:
        try: import wa; wa.close()
        except Exception: pass
        try: os.remove(lock_path)
        except Exception: pass
        os._exit(0)
    obs.join()

def _selftest(root):
    print('SELFTEST START', root, flush=True)
    global SETTLE_TEST; SETTLE_TEST = True
    import shutil as _sh
    ran = []
    fails = []
    def ck(label, ok, extra=''):
        ran.append(label.split()[0])
        if not ok: fails.append(label)
        print(('PASS ' if ok else 'FAIL ') + label + ((' ' + str(extra)) if extra else ''), flush=True)
        return ok
    _tg0 = {t.lower().replace('\u2013','-').replace(' ','_') for t in ['Awaiting CV Update','Awaiting JD Confirmation','Call Scheduled','Feedback Pending','Interview Scheduled','Closed – Not Proceeding','Ready for Manager Review','Rejected by Client']}
    _ROOTTAGS0 = {c for c in os.listdir(root) if os.path.isdir(os.path.join(root, c)) and c.lower().replace('\u2013','-').replace(' ','_') in _tg0}
    B = Butler(root)
    ck('S1 bindings', all(callable(getattr(B, m, None)) for m in ('route','handle_tags','_reconcile_tags','_compact_numbers','position_folder_for','_folder_for_tag')))
    _prw = [os.path.join(dp, f) for dp, dn, fn in os.walk(root) for f in fn if f == 'Pradip Amte.pdf']
    POS = os.path.dirname(os.path.dirname(_prw[0])) if _prw else root
    ck('S2 tag reading', bool(_prw) and os.path.basename(os.path.dirname(_prw[0])) in ('Closed – Not Proceeding','Closed - Not Proceeding'), os.path.basename(os.path.dirname(_prw[0])) if _prw else 'pradip missing')
    B._reconcile_tags(print)
    ck('S3 pradip filed by tag', bool(_prw) and os.path.basename(os.path.dirname(_prw[0])) in ('Closed – Not Proceeding','Closed - Not Proceeding'))
    cands = []
    for _dp, _dn, _fn in os.walk(root):
        _dn[:] = [x for x in _dn if not x.startswith('.') and x.lower() not in ('converted files','converted doc files','duplicates','previous versions')]
        for _f in sorted(_fn):
            _fl = _f.lower()
            if _fl.endswith('.pdf') and not _f.startswith('zz_') and not _fl.startswith('jd') and ' jd' not in _fl and '_jd' not in _fl and not _fl.startswith('regional') and 'location' not in _fl:
                cands.append(os.path.join(_dp, _f)); break
        if cands: break
    tmp = os.path.join(POS, 'zz_garbage_test.pdf')
    ok4 = False
    if cands:
        b0 = os.path.splitext(os.path.basename(cands[0]))[0]
        pre = set(os.listdir(POS))
        _sh.copy(cands[0], tmp)
        B.route(tmp, lambda _m: None)
        ok4 = not os.path.exists(tmp)
        for f in set(os.listdir(POS)) - pre:
            if f.startswith('zz_') or f == b0 + '.pdf' or re.match(re.escape(b0) + r'_\d+\.pdf$', f):
                try: os.remove(os.path.join(POS, f))
                except Exception: pass
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass
    ck('S4 wrong-name repair', ok4)
    _clf = [dd for dd in os.listdir(POS) if dd.lower().startswith('closed')]
    ck('S5 board closed row', bool(_clf) and any(os.path.isfile(os.path.join(POS, dd, f)) for dd in _clf for f in os.listdir(os.path.join(POS, dd))))
    _src = open(__file__).read()
    import ast as _ast
    _ln = _src.split('\n')
    _hcls = [x for x in _ast.walk(_ast.parse(_src)) if isinstance(x, _ast.ClassDef) and x.name == 'H']
    _seg = '\n'.join(_ln[_hcls[0].lineno-1:_hcls[0].end_lineno]) if _hcls else ''
    ck('S6 watcher handler intact', bool(_seg) and 'self._add' in _seg and 'B._add' not in _seg, f'seglen={len(_seg)}')
    _wa = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa.py')).read()
    _br = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'briefing.py')).read()
    ck('S7 wa interactive uses _click_send', 'I clicked send myself' in _wa)
    ck('S8 scan index per-root', 'def _scan_path(num, root=None)' in _br)
    ck('S9 rename swallows vanished files', 'except FileNotFoundError:' in _src)
    ck('S10 prompts silence sweeps', 'INTERACTIVE = False' in _src and 'if not INTERACTIVE:' in _src and 'def hsay(m):' in _src)
    ck('S11 missed works without focus + help card', "'display': clean_pos(os.path.basename(root))," in _br and 'missed  <number>' in _br)
    ck('S12 send phase launches+fills', 'launch_persistent_context' in _wa and 'keyboard.insert_text(text)' in _wa)
    ck('S13 missed phone-first + strip', '_phone_first(arg)' in _br and "arg = (arg or '').strip()" in _br)
    ck('S14 manual-send default', 'I clicked send myself' in _wa)
    ck('S15 autosend constant defined', 'AUTOSEND =' in _wa)
    ck('S16 verified auto-fill', 'def _place_text(' in _wa and 'ok_fill = _place_text(page, text, say)' in _wa)
    ck('S17 playwright import at module scope', 'try:\n    from playwright.sync_api import sync_playwright' in _wa)
    ck('S18 position never falls back to company root', 'return os.path.join(self.root, parts[0], parts[1])' in _src and 'return self.root' not in _src.split('def position_folder_for')[1].split('def ')[0])
    ck('S19 reconcile adds no company-root tag folders', not [c for c in os.listdir(root) if os.path.isdir(os.path.join(root, c)) and c.lower().replace('\u2013','-').replace(' ','_') in _tg0 and c not in _ROOTTAGS0])
    ck('S20 sweep scoping + heat net intact', 'def sweep_dirs(self' in _src and 'n % 9 == 0 or not dirs' in _src)
    ck('S21 stage ageing wired end-to-end', 'self.slog.observe' in _src and "elif cmd == 'history'" in _br and 'def do_stale(' in _br)
    ck('S22 fixphone command routed', 'def do_fixphone(' in _br and "cmd == 'fixphone'" in _br)
    ck('S23 not-on-WhatsApp aborts before gate', "isn't on WhatsApp" in _wa)
    ck('S24 live locks visible at launch', '🔒 live lock: " +' in _src)
    ck('S25 containment refusal at lock acquire', ('\u26d4' + ' refused: live butler') in _src)
    ck('S26 scan index per-root only', "scan_index_' + hashlib" in _br and 'scan_index.json' not in _br.split('def _scan_path')[1].split('def ')[0])
    ck('S27 nudge routes to tree-walk resolver + phones follow moves', 'def _phones_by_basename(' in _br and "for _sr in ([] if hit else [f['path']" in _br)
    ck('S28 learned phone beats extraction', '_phones_by_basename(hit) or phones_of(hit)' in _br)
    ck('S29 download stability gate', (chr(35) + ' DOWNLOAD-STABILITY-GATE') in _src)
    ck('S30 converter refuses empty sources', ('conversion skipped: ' + 'source is 0 bytes') in _src)
    ck('S31 fit ranking sidecar engine', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitrank.py')) and 'fitrank.tick' in _src)
    ck('S32 call/next routed', "cmd == 'call'" in _br)
    ck('S33 fitrank ocr + deep throttle', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitrank.py')) and 'budget = 3' in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitrank.py')).read())
    ck('S34 ledgers live + routed', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) and "cmd == 'case'" in _br)
    ck('S35 heartbeat ticks + scoped reconcile', ('fitrank.' + 'tick(B)') in _src.split('last_hb > 120')[1])
    ck('S36 StageLog not self-recursive', 'self.slog = StageLog(root)' not in _src.split('class StageLog:')[1].split('class Butler:')[0])
    ck('S37 cadence armed + processed', 'cadence.arm(' in _wa and ('cadence.' + 'process(B') in _src)
    ck('S38 outbox/due/ack routed', "cmd == 'outbox'" in _br)
    _led = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''
    ck('S39 ledger hygiene: no utility positions + phone precedence', 'untitled' in _led and 'phone_fixes.json' in _led)
    ck('S40 learned beats extraction at learn-back', '_lb = _phones_by_basename(path)' in _br)
    ck('S41 outbox approve-and-send', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')) and 'def run_outbox(' in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')).read() and 'run_outbox(root' in _br)
    _led2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''
    ck('S42 money brain routed', 'def show_money(' in _led2 and "cmd == 'money'" in _br)
    ck('S43 incentive formula constant', ('INC_RATE = 0.5 * 0.0833') in _led2)
    _led3 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''
    ck('S44 ledger prunes stale positions', (chr(35) + ' LEDGER-PRUNE') in _led3)
    _wr = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'waread.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'waread.py')) else ''
    ck('S45 recorder is read-only', bool(_wr) and not any(w in _wr for w in ('_click_send', 'insert_text', 'compose-btn-send', 'keyboard.press')))
    _sem = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sem.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sem.py')) else ''
    ck('S46 semantic + ghost + client routed', 'def similar(' in _sem and 'def ghost(' in _sem and "cmd == 'ghost'" in _br)
    ck('S47 ghost reads conversations only', 'conversations.json' in _sem and 'send_review' not in _sem)
    _led4 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''
    ck('S48 digest + bookends', 'def show_digest(' in _led4 and 'interview_eve' in _led4 and "cmd == 'digest'" in _br)
    _cad2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')) else ''
    ck('S49 cadence queue accepts due', 'due=None' in _cad2)
    ck('S50 summarize routed', 'def do_summarize(' in _br and "cmd == 'summarize'" in _br)
    ck('S51 drafts use position/client truth', 'def _pos_client_for(' in _br and 'def _fmt_tpl(' in _br and "position=f['display']" not in _br)
    ck('S52 client alias command routed', 'def do_clientname(' in _br and "cmd == 'clientname'" in _br)
    _tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_template.txt')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_template.txt')) else ''
    ck('S53 professional template live', 'Sundeep Rana' in _tpl and ('{where}' in _tpl or '{where_line}' in _tpl) and 'where=at' in _br)
    ck('S54 position/location split wired', 'def _split_pos(' in _br and 'def _fmt_tpl(' in _br)
    _td = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    ck('S55 scenario templates + kind-aware outbox', os.path.isdir(_td) and len([f for f in os.listdir(_td) if f.endswith('.txt')]) >= 9 and '_fmt_tpl(base,' in _cad2)
    ck('S56 log trim + single helper defs', (chr(35) + ' LOG-TRIM') in _src and _br.count('def _pick_model(') == 1)
    _tm = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'missed.txt')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'missed.txt')) else ''
    ck('S57 unified voice + emojis', 'Regards,' in _tm and '📞' in _tm and 'where=at' in _br)
    ck('S58 nudge speaks awaiting voice', "words=['awaiting', 'confirmation']" in _br and 'def do_missed(arg, root, say=print, ask=None, words=None)' in _br)
    ck('S58 brace-proof drafts', 'class _SafeDict' in _br and 'where=at' in _br)
    ck('S59 nudge speaks awaiting voice', "'nudge': 'awaiting'" in _br and "TPL_DIR, 'awaiting.txt')" in _br)
    ck('S60 stage-aware follow', 'def _stage_words(' in _br and "cmd == 'follow'" in _br)
    ck('S61 q never counts as sent', 'left in field & window closed' in _wa)
    ck('S62 tpltest + split hardening', 'def do_tpltest(' in _br and (chr(35) + ' SPLIT-HARD') in _br)
    ck('S63 referral voice for closed candidates', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'referral.txt')) and "cmd == 'refer'" in _br and "'closed' in st: return ['referral']" in _br)
    ck('S64 referral voice not shadowed', "'referral': 'reference'" not in _br and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'referral.txt')))
    ck('S65 chat ctrl-c graceful', 'except KeyboardInterrupt:' in _br.split('q = input("you> ")')[1][:300])
    _body = _src.split('def _selftest')[0]
    ck('S66 settle-gate on every mutating door', 'def _settling(' in _src and all(_body.count(m) == 1 for m in (chr(35)+' ROUTE-GATE', chr(35)+' TAGS-GATE', chr(35)+' RECONCILE-GATE')))
    ck('S67 heal sweep + debris archive', 'def _heal(' in _src and 'download_debris' in _src and 'B._heal(hsay)' in _src.split('last_hb > 120')[1])
    try: B._snapshot(hsay)  # SNAPSHOT-CALL v69.2
    except Exception: pass
    ck('S68 selftest opens settle-gates', 'SETTLE_TEST = True' in _src and 'if SETTLE_TEST: return False' in _src)
    _rg = _src.split('def _reconcile_tags')[1].split('\ndef ')[0]
    ck('S69 rename hands gated', (chr(35)+' RENAME-GATE') in _src and (chr(35)+' NORM-GATE') in _src)
    ck('S70 reconcile dedupes instead of skipping', 'while os.path.exists(dst): dst = os.path.join(tgt,' in _rg and 'if os.path.exists(dst): continue' not in _rg)
    ck('S71 rename breaker resets on name change', 'self.rcn' in _src.split('def handle_pdf')[1].split('def ')[0])
    ck('S72 settle-fast + pending drain', (chr(35)+' SETTLE-FAST') in _src and (chr(35)+' DRAIN-PENDING') in _src and 'def _drain_pending(' in _src)
    ck('S73 fast xattr tag reads + protocol order', 'def _has_tag_xattr(' in _src and 'def _tags_of_fast(' in _src and (chr(35)+' TAGS-FIRST') not in _src)
    ck('S74 worker-door journal skip', (chr(35)+' WORK-DOOR SKIP') in _src and 'B._jload()' in _src)
    ck('S75 tag poll catches silent re-tags', 'def _tag_poll(' in _src and (chr(35)+' TAG-POLL') in _src and _src.count(chr(35)+' TAG-POLL') >= 2)
    ck('S76 reconcile reads tags without mdls', _src.split('def _reconcile_tags')[1].split('\ndef ')[0].count('_tags_of_fast(') >= 1)
    _pdfseg = _src.split("elif ext == '.pdf':")[1].split('elif ext ==')[0]
    ck('S77 PROTOCOL rename-then-move for CVs', _pdfseg.index('self.handle_pdf(') < _pdfseg.index('self.handle_tags(') and (chr(35)+' TAGS-FIRST') not in _pdfseg)
    ck('S78 heal retries + reconcile rename-first', (chr(35)+' HEAL-RETRY') in _src and (chr(35)+' RENAME-FIRST') in _src)
    ck('S79 suffix-stable renames, self slot free', (chr(35)+' SUFFIX-STABLE') in _src and _src.count(chr(35)+' SELF-FREE') >= 2)
    ck('S80 one ack clock per send', _wa.count('_arm(digits, text)') == 2)
    ck('S82 heal un-disarms rename breaker', (chr(35)+' RC-FRESH') in _src and '< 30: continue  # HEAL-RETRY' in _src)
    ck('S83 renwhy X-ray routed', 'def do_renwhy(' in _br and "cmd == 'renwhy'" in _br)
    ck('S84 clean_pos strips pipes', (chr(35)+' PIPE-CLEAN') in _br)
    ck('S85 cadence never queues twins', 'def _collapse(' in _cad2 and _cad2.count('_collapse(d)') >= 3)
    ck('S86 cloud snapshot habit', (chr(35)+' SNAPSHOT') in _src and 'B._snapshot(' in _src)
    _sn = 'B._snapshot(' + 'hsay)'; _hl = 'B._heal(' + 'hsay)'
    ck('S87 snapshot call lives in heartbeat', _src.count(_sn) == 1 and _src.rindex(_sn) > _src.rindex(_hl))
    ck('S88 extension-less files get sniffed', 'def _sniff_ext(' in _src and (chr(35)+' SNIFF-EXT') in _src and _src.count('_sniff_ext(') >= 2)
    ck('S89 rename and move in one pass', (chr(35)+' INODE-RELINK') in _src and sum(1 for L in _src.split(chr(10)) if (chr(35)+' TAG-POLL') in L and ('> 8:' in L or '> 15:' in L)) == 0)
    ck('S90 summary xlsx canon everywhere', (chr(35)+' SUMMARY-CANON') in _src and (chr(35)+' SUMMARY-CALL') in _src and 'def _summary_xlsx(' in _src)
    ck('S91 stranded retry at thirty seconds', (chr(60)+' 30: continue  '+chr(35)+' HEAL-RETRY') in _src)
    ck('S92 client-root tag filing', (chr(35)+' CLIENT-ROOT') in _src and 'client root)' in _src)
    ck('S93 heal sniffs extension-less files', (chr(35)+' HEAL-SNIFF') in _src and _src.count('_sniff_ext(') >= 3)
    ck('S94 client-root block on live path', _src.index('def handle_tags') < _src.index(chr(35)+' CLIENT-ROOT v73') < _src.index('split(os.sep)) < 2: return'))
    ck('S95 tag-skip is per-call not per-instance', 'skip_tags=None' in _src and _src.count('skip_tags=False') >= 2 and (chr(35)+' SKIP-FIX') in _src)
    ck('S96 tag-truth filing, no whitelist', (chr(35)+' TAG-TRUTH') in _src)
    ck('S97 heal and drain read tags per call', _src.count('skip_tags=False') >= 2)
    ck('S98 pulse cannot kill the watcher', (chr(35)+' LOOP-ARMOUR') in _src and 'butler_alive.stamp' in _src and 'pulse skipped' in _src)
    ck('S99 reconcile never nests a stage in itself', (chr(35)+' ALREADY-FILED') in _src and _src.split('def _reconcile_tags')[1].split('\ndef ')[0].count(chr(35)+' ALREADY-FILED') == 1)
    ck('S100 tag-truth is the only filing voice', (chr(35)+' HOME v78') in _src and (chr(35)+' TAG-TRUTH-AUTHORITATIVE') in _src)
    ck('S101 learned names beat document names', 'def _names_by_phone(' in _src and (chr(35)+' NAME-BY-PHONE') in _src and 'import fitrank as _fr' in _src)
    ck('S102 name command learns and renames on demand', 'def do_name(' in _br and "cmd == 'name'" in _br)
    ck('S103 chat stays read-only', (chr(35)+' CHAT-READONLY') in _br and sum(1 for L in _br.split(chr(10)) if 'do_name(' in L and not L.strip().startswith('def do_name') and not L.strip().startswith('elif cmd ==')) == 0)
    ck('S104 butler learns manual renames', (chr(35)+' LEARN-BACK v80.1') in _src)
    _vm = json.load(open(os.path.join(BASE_DIR, 'tag_voices.json')))
    ck('S105 tag voice map has no internal stages', 'Ready for Manager Review' not in _vm and len(_vm) >= 7)
    ck('S106 autodraft never sends', '.send(' not in _src.split('def _autodraft_tick')[1].split('def _heal')[0] and '_click_send' not in _src.split('def _autodraft_tick')[1].split('def _heal')[0])
    ck('S107 toggle honoured', 'autodraft.flag' in _src and 'briefing.py chat' in _src and (chr(35)+' AUTODRAFT') in _src)
    ck('S108 drafts go through the signed wa door', 'wa.send_review(' in _src and 'import wa' in _src)
    ck('S109 autodraft silence explains itself', (chr(35)+' AD-VISIBILITY') in _src and 'no position folder' in _src)
    ck('S110 autodraft log reachable from chat', 'def do_adlog(' in _br and "cmd == 'adlog'" in _br and (chr(35)+' ADLOG') in _br)
    ck('S111 pulse clock uses the module global clock', ('_t' + '.time()') not in _src and 'import time' in _src)
    ck('S112 drafts fire in their own process', (chr(35)+' AD-FIRE v81.5') in _src and 'threading.Thread' not in _src.split('def _ad_fire')[1].split('def _draft_one')[0])
    ck('S113 every tag-add is witnessed', (chr(35)+' TAGADD-LOG') in _src)
    ck('S114 the pulse has a voice', (chr(35)+' PULSE-WITNESS') in _src and (chr(35)+' TICK-WITNESS') in _src)
    ck('S115 tags read through macOS libc', 'def _xattr_raw(' in _src and ('os.get' + 'xattr(') not in _src and (chr(35)+' XATTR-RAW') in _src)
    ck('S116 the log speaks instantly', (chr(35)+' LOG-FLUSH') in _src and 'line_buffering' in _src)
    ck('S117 headless butler loops instead of listening', (chr(35)+' HEADLESS-FIX') in _src and 'sys.stdout.isatty()' in _src)
    ck('S118 the REPL cannot park or kill the loop', (chr(35)+' HEADLESS-INPUT') in _src and 'builtins' in _src)
    ck('S119 the REPL door keys on INTERACTIVE', (chr(35)+' REPL-GATE v81.12') in _src and ('if sys.stdin' + '.isatty():') not in _src)
    ck('S121 the pulse thread owns its clock', (chr(35)+' PULSE-CLOCK') in _src and 'pulse thread armed' in _src)
    ck('S122 exactly one late pulse start', _src.count('Thread(target=' + '_pulse_loop') == 1 and (chr(35)+' PULSE-START-LATE') in _src)
    ck('S123 no ghost clock alias', ('_t' + '.time()') not in _src and ('_t' + '.sleep(') not in _src)
    ck('S124 phones read from the path, not from prose', 'phones_of(fp)' in _src and ('phones_of(fitrank' + '._text') not in _src and ('phones_of(_fr' + '._text') not in _src)
    ck('S125 re-apply and multi-number draft', (chr(35)+' RETOUCH') in _src and (chr(35)+' MULTI-NUM') in _src)
    ck('S126 the poll sees trace-less tag edits', (chr(35)+' CTIME-EYE') in _src and 'st_ctime' in _src)
    ck('S127 the window waits for your thumb', (chr(35)+' WA-WAIT v81.24') in _src and os.path.exists(os.path.join(BASE_DIR, 'ad_wait.py')))
    ck('S128 the queue advances on your send', (chr(35)+' SEND-AWARE') in _src and 'ad_state.json' in _src)
    ck('S129 ad_wait knows load-silence from closed windows', open(os.path.join(BASE_DIR, 'ad_wait.py')).read().count('seen_alive') > 0)
    ck('S130 closed or sent marks the round done', (chr(35)+' DONE-MARK v81.26') in _src and (chr(35)+' KIND v81.26') in _src)
    ck('S131 queued drafts speak fresh wording', (chr(35)+' FRESH-TEXT v81.26') in _src and 'build_text' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S132 fidgeting is a switch, not a fate', (chr(35)+' FIDGET') in _src and os.path.exists(os.path.join(BASE_DIR, 'fidget.flag')))
    ck('S133 one window serves the whole queue', 'pop_job' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and 'autodraft_queue.json' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S134 the poll remembers across restarts', (chr(35)+' BASELINE-PERSIST') in _src and 'tag_baseline.json' in _src)
    ck('S136 the window slides on arrival and release speaks', 'AD-WAIT v81.3' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and (chr(35)+' RELEASE-VOICE v81.32') in _src)
    ck('S137 no ownerless windows survive a relaunch', (chr(35)+' STALE-WINDOW-SWEEP') in _src and (chr(35)+' TAB-CLEAN') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S138 a dead watcher never blocks the queue', (chr(35)+' PID-ALIVE v81.34') in _src and (chr(35)+' SWEEP-RESET v81.34') in _src and 'os.getpid()' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S139 one fire per tick, no profile races', (chr(35)+' HELD v81.35') in _src and ('self._ad_held = time.time() ' + '+ 90') in _src)
    ck('S140 one release per state change', (chr(35)+' SINGLE-FLIGHT v81.35') in _src and ('def _ad_' + 'claim') in _src)
    ck('S141 the window opens in seconds, not a minute', os.path.exists(os.path.join(BASE_DIR, 'wa_warm.py')) and 'connect_over_cdp' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S142 stale field text is cleared before placement', 'CLEAR-BEFORE-PLACE v81.37' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S143 only ownerless browsers are swept', (chr(35)+' OWNER-AWARE v81.38') in _src and 'wa_warm.py' in _src)
    ck('S144 the tick never dies on an uninitialised queue', (chr(35)+' Q-INIT v81.40') in _src)
    ck('S145 one owned warm browser, self-healing', (chr(35)+' WARM-RETRY v81.40') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and 'is_connected' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read())
    ck('S146 your close is honoured for ten minutes', 'WARM-COOLDOWN v81.41' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read() and (chr(35)+' FAST-FALLBACK v81.41') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S147 the warm browser is kept alive unless you closed it', (chr(35)+' WARM-KEEPALIVE v81.44') in _src and 'wa_warm_closed.ts' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read())
    ck('S148 ctime-only touches are quiet unless fidget is on', (chr(35)+' KIND-RESPECT v81.44') in _src)
    ck('S149 no doubled drafts', (chr(35)+' DEDUPE v81.44') in _src and (chr(35)+' CLEAR-IN-SLIDE v81.44') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S150 the keeper may die but may not flicker', (chr(35)+' BREAKER v81.45') in open(os.path.join(BASE_DIR, 'wa_warm.py')).read() and (chr(35)+' WARM-SUPERVISOR v81.45') in _src)
    ck('S151 stale jobs expire and the field dedupes', (chr(35)+' STALE-JOB-PRUNE v81.45') in _src and (chr(35)+' DEDUPE-FIELD v81.45') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())
    ck('S152 the keeper probes closure instead of assuming an API', 'browser.is_connected' not in open(os.path.join(BASE_DIR, 'wa_warm.py')).read() and (chr(35)+' CLOSE-WATCH v81.46') in open(os.path.join(BASE_DIR, 'wa_warm.py')).read())
    ck('S153 download scars are stripped from names', (chr(35)+' DASH-CLEAN v81.48') in _src and 'rename-clean' in _src)
    missing = [f'S{n}' for n in range(1, 20) if f'S{n}' not in ran]
    if missing: print('SKILLS MISSING', missing, flush=True)
    if fails or missing: return False
    print('ALL GREEN', flush=True)
    return True

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--selftest':
        sys.exit(0 if _selftest(sys.argv[2]) else 1)
    main()
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
INTERACTIVE = False
def _git_stamp():
    try:
        r = subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, timeout=5)
        return (r.stdout or '').strip() or 'nogit'
    except Exception:
        return 'nogit'
GIT_STAMP = _git_stamp()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(BASE_DIR, "butler.lock")
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
def _tags_from_plist(path):
    try:
        import plistlib
        data = os.getxattr(path, 'com.apple.metadata:_kMDItemUserTags')
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
                tg = os.getxattr(p, 'com.apple.metadata:_kMDItemUserTags')
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
        if name and f"{name}.pdf" != base:
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
    def _route(self, p, say):
        if p.lower().endswith('.tmp.html'):
            try:
                if time.time() - os.path.getmtime(p) > 600:
                    os.remove(p)
                    say(f"\n🧹 [clean] removed stale temp: {os.path.basename(p)}")
            except Exception:
                pass
            return
        ext = os.path.splitext(p)[1].lower()
        if ext in ('.doc', '.docx', '.msg'):
            pdf = self.handle_convert(p, say)
            if pdf and os.path.exists(pdf):
                self.handle_pdf(pdf, say)
                if not getattr(self, '_skip_tags', False): self.handle_tags(pdf, say)
        elif ext == '.pdf':
            p = self.normalize_suffix(p, say)
            self.handle_pdf(p, say)
            if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)
            self._compact_numbers(os.path.dirname(p), say)
        elif ext == '.xlsx':
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
        if len(os.path.relpath(os.path.dirname(p), self.root).split(os.sep)) < 2: return
        T = get_tags(p)
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
                    T = get_tags(fp)
                    tag = None
                    for t in T:
                        if _n(t) in known: tag = known[_n(t)]; break
                    if not tag: continue
                    tgt = self._folder_for_tag(self.position_folder_for(fp), tag)
                    if os.path.abspath(os.path.dirname(fp)) == os.path.abspath(tgt): continue
                    os.makedirs(tgt, exist_ok=True)
                    dst = os.path.join(tgt, f)
                    if os.path.exists(dst): continue
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
        if sys.stdin.isatty():
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
    _console_start()

    last_full = time.time(); last_hb = time.time(); last_clean = time.time(); n = 0
    try:
        while True:
            import time as _t
            B._n = getattr(B, '_n', 0) + 1
            if B._n > 3 and (_t.time() - getattr(B, '_last_sweep', 0)) < 120:
                with dlock:
                    _ip = list(dirty); dirty.clear()
                for p in _ip: ex.submit(work, p)
                if getattr(B, '_jdirty', False):
                    B._jsave(); B._jdirty = False
                _t.sleep(2); continue   # idle: events drained every tick
            B._last_sweep = _t.time()
            if B._n == 4:
                print('😴 idle mode: event-driven now · safety sweep every 10 min')
            time.sleep(1)
            with dlock:
                paths = list(dirty); dirty.clear()
            for p in paths: ex.submit(work, p)
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
    ck('S53 professional template live', 'Sundeep Rana' in _tpl and '{where_line}' in _tpl)
    ck('S54 position/location split wired', 'def _split_pos(' in _br and 'def _fmt_tpl(' in _br)
    _td = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    ck('S55 scenario templates + kind-aware outbox', os.path.isdir(_td) and len([f for f in os.listdir(_td) if f.endswith('.txt')]) >= 9 and '_fmt_tpl(base,' in _cad2)
    ck('S56 log trim + single helper defs', (chr(35) + ' LOG-TRIM') in _src and _br.count('def _pick_model(') == 1)
    missing = [f'S{n}' for n in range(1, 20) if f'S{n}' not in ran]
    if missing: print('SKILLS MISSING', missing, flush=True)
    if fails or missing: return False
    print('ALL GREEN', flush=True)
    return True

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--selftest':
        sys.exit(0 if _selftest(sys.argv[2]) else 1)
    main()
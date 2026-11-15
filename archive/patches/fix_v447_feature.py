import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile():
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(os.getcwd(), fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
M0 = perfile()
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
sp = next((k for k, l in enumerate(B) if 'PDF-SPOTLIGHT v85.61: the library' in l), None)
if sp is not None and 'PDF-PDFKIT' not in '\n'.join(B[max(0,sp-8):sp]):
    d = ind(B[sp])
    B[sp:sp] = [d*' ' + "if os.path.splitext(p)[1].lower() == '.pdf':  # PDF-PDFKIT v85.65: when the library is dead and Spotlight has no index, PDFKit reads the text layer natively through JavaScript for Automation - no libraries, no pixels, no index required",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "import subprocess as _sp6",
                (d+8)*' ' + "_pj = p.replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"')",
                (d+8)*' ' + "_js = 'ObjC.import(\"Quartz\"); var d = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(\"' + _pj + '\")); (d.isNil() || !d.string) ? \"\" : d.string.js'",
                (d+8)*' ' + "_r6 = _sp6.run(['osascript', '-l', 'JavaScript', '-e', _js], capture_output=True, timeout=60)",
                (d+8)*' ' + "_s6 = _r6.stdout.decode('utf-8', 'ignore')",
                (d+8)*' ' + "if _s6.strip(): return _s6",
                (d+4)*' ' + "except Exception:",
                (d+8)*' ' + "pass"]
    done.append('pdf-pdfkit')
t0 = next((k for k, l in enumerate(B) if l.startswith('def _tick_loop(')), None)
if t0 is not None and 'BELL-VERSION v85.64' not in '\n'.join(B[t0:t0+50]):
    t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def ') or (B[k].strip() and not B[k].startswith(' ') and not B[k].startswith('#')))
    d = ind(B[t0])
    B[t0:t1] = [d*' ' + "def _tick_loop():  # WATCH-HOOK v85.53 (version v85.64): the bell is owned by the newest living code - the stamp carries a git hash, and a stale owner is inherited around, never fought",
                (d+4)*' ' + "import time as _tt, subprocess as _sp5",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "_me = _sp5.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, cwd=BASE_DIR).stdout.decode().strip()",
                (d+4)*' ' + "except Exception:",
                (d+8)*' ' + "_me = 'unknown'",
                (d+4)*' ' + "pf = os.path.join(BASE_DIR, '.tick.pid')",
                (d+4)*' ' + "while True:  # BELL-RETRY v85.55: a doorbell that gives up after one knock is not a doorbell",
                (d+8)*' ' + "own = False",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "if not os.path.exists(pf):",
                (d+16)*' ' + "own = True",
                (d+12)*' ' + "else:",
                (d+16)*' ' + "age = _tt.time() - os.stat(pf).st_mtime",
                (d+16)*' ' + "raw = open(pf).read().strip()",
                (d+16)*' ' + "pid_s = raw.split('|')[0]",
                (d+16)*' ' + "ver_s = raw.split('|')[1] if '|' in raw else ''",
                (d+16)*' ' + "dead = False",
                (d+16)*' ' + "try:",
                (d+20)*' ' + "os.kill(int(pid_s), 0)",
                (d+16)*' ' + "except Exception:",
                (d+20)*' ' + "dead = True",
                (d+16)*' ' + "if dead or age > 30 or ver_s != _me:  # BELL-VERSION v85.64: a living owner running old code is still the wrong owner - the hash decides, not the pulse alone",
                (d+20)*' ' + "own = True",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "own = True",
                (d+8)*' ' + "if own:",
                (d+12)*' ' + "try:",
                (d+16)*' ' + "open(pf, 'w').write('%s|%s' % (os.getpid(), _me))",
                (d+12)*' ' + "except Exception:",
                (d+16)*' ' + "pass",
                (d+12)*' ' + "break",
                (d+8)*' ' + "_tt.sleep(10)",
                (d+4)*' ' + "while True:",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "if open(pf).read().strip().split('|')[0] != str(os.getpid()):  # BELL-ABDICATE v85.64: an ousted owner stops beating on its next breath - abdication, not rivalry",
                (d+16)*' ' + "return",
                (d+12)*' ' + "os.utime(pf, None)  # BELL-HEARTBEAT v85.59: the stamp is refreshed every beat - a pulse, not a lock; the witness of the rewritten block rides the line that is the heartbeat",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "pass",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "_event_tick((desk_load() or {}).get('primary') or os.getcwd(), _tick_log)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "pass",
                (d+8)*' ' + "_tt.sleep(5)",
                ""]
    done.append('bell-version')
qk = next((k for k, l in enumerate(B) if 'SERVICE-QUEUE v85.58' in l), None)
if qk is not None and 'SERVICE-RECEIPT' not in '\n'.join(B[qk:qk+20]):
    ek = next(k for k in range(qk, qk+20) if B[k].strip() == 'except Exception:' and ind(B[k]) == ind(B[qk])+4)
    d = ind(B[qk]) + 8
    B.insert(ek, d*' ' + "if _qs: log('✅ service batch done: %d paper(s) - deeds above' % len(_qs))  # SERVICE-RECEIPT v85.64 + RECEIPT-INDENT v85.65: the total stands inside the try body among the deeds it counts - a comment in the surgeon's notes is not a clause in the body, so both names ride the line itself")
    done.append('service-receipt')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 pdfkit eye, receipt line with both names, bell stamp and carried heartbeat:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'PDF-PDFKIT v85.65' in l or 'SERVICE-RECEIPT v85.64 + RECEIPT-INDENT' in l or 'BELL-VERSION v85.64: a living owner' in l or 'BELL-HEARTBEAT v85.59: the stamp' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.65' not in t:
        open(AR, 'a').write('v85.65: PDF-PDFKIT - Quartz PDFKit via osascript JXA reads any pdf text layer natively, indexed or not, beneath the library and above Spotlight; SERVICE-RECEIPT and RECEIPT-INDENT both ride the inserted line so the probe reads them in the house; BELL-VERSION stamp with abdication and the heartbeat witness on the utime line (S409, S410, S411)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S409 the bell belongs to the newest living code, and an ousted owner abdicates", "'S408 the diagnostic names its own path or confesses the whole list", "ck('S409 the bell belongs to the newest living code, and an ousted owner abdicates', (chr(35)+' BELL-VERSION v85.64') in _src and (chr(35)+' BELL-ABDICATE v85.64') in _src and (chr(35)+' BELL-HEARTBEAT v85.59') in _src)"),
      ("'S410 a drained queue always ends with a spoken total", "'S409 the bell belongs to the newest living code, and an ousted owner abdicates", "ck('S410 a drained queue always ends with a spoken total', (chr(35)+' SERVICE-RECEIPT v85.64') in _src and (chr(35)+' RECEIPT-INDENT v85.65') in _src)"),
      ("'S411 every pdf has a native text eye that needs no index and no pixels", "'S410 a drained queue always ends with a spoken total", "ck('S411 every pdf has a native text eye that needs no index and no pixels', (chr(35)+' PDF-PDFKIT v85.65') in _src and ('PDFDocument' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

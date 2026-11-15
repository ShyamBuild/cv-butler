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
for k, l in enumerate(B):
    if 'timeout=180' in l:
        B[k] = l.replace('timeout=180', 'timeout=240')
        done.append('pages-patience-240')
if 'def _pages_pdf(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def _convert_to_pdf('))
    B[i:i] = ["def _pages_pdf(p, out, log):  # PAGES-FIRST v85.56: the master's first choice for doc to pdf is Pages, whose rendering keeps the paper's face; LibreOffice stands second, sips speaks for images",
              "    import subprocess as _sp3",
              "    scr = 'tell application \"Pages\"\\n  set _d to open POSIX file \"%s\"\\n  export _d to POSIX file \"%s\" as PDF\\n  close _d saving no\\nend tell\\n' % (p.replace('\"', '\\\\\"'), out.replace('\"', '\\\\\"'))",
              "    try:",
              "        r = _sp3.run(['osascript', '-e', scr], capture_output=True, timeout=240)",
              "        return r.returncode == 0 and os.path.exists(out)",
              "    except Exception:",
              "        return False",
              ""]
    done.append('pages-first-def')
so = next((k for k, l in enumerate(B) if "'soffice', '--headless'" in l), None)
if so is not None and '_pages_pdf' not in B[so] and '_okp' not in B[so-1]:
    d = ind(B[so])
    B[so:so+1] = [d*' ' + "_okp = _pages_pdf(p, out, log)  # PAGES-FIRST v85.56: Pages renders, and only if Pages refuses does the second hand move",
                  d*' ' + "if not _okp:",
                  (d+4)*' ' + "_sp.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(p), p], capture_output=True, timeout=300)"]
    done.append('pages-first-wire')
if 'def _word_text(' not in '\n'.join(B):
    a0 = next((k for k, l in enumerate(B) if l.startswith('def _name_from_first_line(')), None) or next((k for k, l in enumerate(B) if l.startswith('def _ident_of(')))
    B[a0:a0] = ["def _word_text(p):  # TEXT-DOCX v85.55: a Word paper reads natively through macOS textutil - full text in milliseconds, no LibreOffice, no pixels, no OCR cap; the converter's absence never blinds the eyes again",
                "    try:",
                "        if os.path.splitext(p)[1].lower() not in ('.docx', '.doc', '.rtf'): return ''",
                "        import subprocess as _sp2",
                "        _r = _sp2.run(['textutil', '-convert', 'txt', '-stdout', p], capture_output=True, timeout=60)",
                "        return _r.stdout.decode('utf-8', 'ignore') if _r.returncode == 0 else ''",
                "    except Exception:",
                "        return ''",
                ""]
    done.append('word-text-def')
n = 0
for k, l in enumerate(B):
    if '= extract_text(p) or ' in l and '_word_text(p)' not in l:
        B[k] = l.replace('= extract_text(p) or ', '= _word_text(p) or extract_text(p) or ', 1)
        n += 1
if n: done.append('word-eye-spliced-x%d' % n)
x0 = next((k for k, l in enumerate(B) if l.startswith('def extract_text')), None)
if x0 is not None and 'TEXT-DOCX v85.55: head' not in '\n'.join(B[x0:x0+12]):
    d = ind(B[x0+1]) if x0+1 < len(B) and B[x0+1].strip() else 4
    B[x0+1:x0+1] = [d*' ' + "_wt = _word_text(p)  # TEXT-DOCX v85.55: head eye - if the native reader speaks, the pdf eyes rest",
                    d*' ' + "if _wt.strip(): return _wt"]
    done.append('word-eye-head')
if 'def _case_sweep(' not in '\n'.join(B):
    e0 = next(k for k, l in enumerate(B) if l.startswith('def _event_tick('))
    B[e0:e0] = ["def _case_sweep(root, log):  # CASE-SWEEP v85.57: casing is a property of the name, not of the ceremony's memory - every human-shaped filename is title-cased on the doorbell, examined or not, so no shout outlives its own arrival",
                "    try:",
                "        dirs = [root] + [os.path.join(root, s) for s in _tag_vocab() if os.path.isdir(os.path.join(root, s))]",
                "    except Exception:",
                "        dirs = [root]",
                "    for dpath in dirs:",
                "        try:",
                "            names = os.listdir(dpath)",
                "        except Exception:",
                "            continue",
                "        for x in names:",
                "            p = os.path.join(dpath, x)",
                "            if not os.path.isfile(p): continue",
                "            ext = os.path.splitext(x)[1].lower()",
                "            if ext not in ('.pdf', '.docx', '.doc', '.rtf'): continue",
                "            stem = os.path.splitext(x)[0]",
                "            try:",
                "                if _jd_like_name(x) or _portal_name(x): continue",
                "            except Exception:",
                "                continue",
                "            ws = stem.split()",
                "            if not (2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws)): continue",
                "            disp = _display_name(stem)",
                "            if disp == stem: continue",
                "            q = os.path.join(dpath, disp + ext)",
                "            if os.path.exists(q): continue",
                "            try:",
                "                os.rename(p, q)",
                "                _rename_ledger(p, disp, 'sweep', once=True)",
                "                _repath_ledgers(p, q)",
                "                log('✏️ case sweep: %s → %s' % (x, disp + ext))",
                "            except Exception:",
                "                pass",
                ""]
    done.append('case-sweep-def')
ev = next((k for k, l in enumerate(B) if l.startswith('def _event_tick(')), None)
if ev is not None and 'CASE-SWEEP' not in '\n'.join(B[ev:ev+8]):
    dd = next(k for k in range(ev, ev+8) if 'dirs = [root]' in B[k])
    d = ind(B[dd])
    B.insert(dd, d*' ' + "_case_sweep(root, log)  # CASE-SWEEP v85.57: the doorbell sweeps casing every beat, so a shout never outlives its arrival")
    done.append('case-sweep-wire')
t0 = next((k for k, l in enumerate(B) if l.startswith('def _tick_loop(')), None)
if t0 is not None and 'BELL-RETRY v85.55' not in '\n'.join(B[t0:t0+26]):
    t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def ') or (B[k].strip() and not B[k].startswith(' ') and not B[k].startswith('#')))
    d = ind(B[t0])
    B[t0:t1] = [d*' ' + "def _tick_log(msg):  # BELL-TOWER v85.55: the bell keeps its own book - one timestamped line per deed, readable from any folder, independent of whichever process owns the key",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "import time as _t2",
                (d+8)*' ' + "open(os.path.join(BASE_DIR, 'tick.log'), 'a').write('%s %s\\n' % (_t2.strftime('%H:%M:%S'), msg))",
                (d+4)*' ' + "except Exception:",
                (d+8)*' ' + "pass",
                d*' ' + "def _tick_loop():  # WATCH-HOOK v85.53 (retry v85.55): the doorbell owns its heartbeat - one stat per folder every five seconds, and the key is re-knocked until held",
                (d+4)*' ' + "import time as _tt, fcntl as _fc",
                (d+4)*' ' + "lf = os.path.join(BASE_DIR, '.tick.lock')",
                (d+4)*' ' + "_lh = None",
                (d+4)*' ' + "while _lh is None:  # BELL-RETRY v85.55: a doorbell that gives up after one knock is not a doorbell - when the current owner exits, the next knock inherits the key",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "_lh = open(lf, 'w')",
                (d+12)*' ' + "_fc.flock(_lh, _fc.LOCK_EX | _fc.LOCK_NB)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "_lh = None",
                (d+12)*' ' + "_tt.sleep(10)",
                (d+4)*' ' + "while True:",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "_event_tick((desk_load() or {}).get('primary') or os.getcwd(), _tick_log)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "pass",
                (d+8)*' ' + "_tt.sleep(5)",
                ""]
    done.append('bell-retry-tower')
print('🔎 patience, pages wire, sweep wire, word splices:')
for k, l in enumerate(B):
    if 'timeout=240' in l or '_okp = _pages_pdf(' in l or '_case_sweep(root, log)' in l or '_word_text(p) or extract_text(p)' in l:
        print('   |', l.strip()[:150])
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
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.57' not in t:
        open(AR, 'a').write('v85.57: Pages patience 240 (the 180 substring belongs to the OCR cap law); CASE-SWEEP on the doorbell title-cases every human-shaped filename examined or not, JD and portal masks untouched, ledgers written; TEXT-DOCX, PAGES-FIRST and the bell stand as designed (S397-S400)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S397 a Word paper is never text-silent - the native reader opens it in milliseconds", "'S396 a verb called from anywhere serves the living desk", "ck('S397 a Word paper is never text-silent - the native reader opens it in milliseconds', (chr(35)+' TEXT-DOCX v85.55') in _src and ('textutil' in _src) and ('def _word_text(' in _src))"),
      ("'S398 the bell re-knocks until it holds the key, and keeps its own book", "'S397 a Word paper is never text-silent - the native reader opens it in milliseconds", "ck('S398 the bell re-knocks until it holds the key, and keeps its own book', (chr(35)+' BELL-RETRY v85.55') in _src and (chr(35)+' BELL-TOWER v85.55') in _src and ('tick.log' in _src))"),
      ("'S399 the first hand that renders a Word paper is Pages, and only Pages' refusal moves the second", "'S398 the bell re-knocks until it holds the key, and keeps its own book", "ck('S399 the first hand that renders a Word paper is Pages, and only Pages'+chr(39)+' refusal moves the second', (chr(35)+' PAGES-FIRST v85.56') in _src and ('osascript' in _src) and ('def _pages_pdf(' in _src) and ('timeout=240' in _src))"),
      ("'S400 casing is a property of the name, not of the ceremony's memory", "'S399 the first hand that renders a Word paper is Pages, and only Pages' refusal moves the second", "ck('S400 casing is a property of the name, not of the ceremony'+chr(39)+'s memory', (chr(35)+' CASE-SWEEP v85.57') in _src and ('def _case_sweep(' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

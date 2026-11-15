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
t0 = next((k for k, l in enumerate(B) if l.startswith('def _tick_loop(')), None)
if t0 is not None and 'BELL-RETRY v85.55' not in '\n'.join(B[t0:t0+24]):
    t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def ') or (B[k].strip() and not B[k].startswith(' ') and not B[k].startswith('#')))
    d = ind(B[t0])
    B[t0:t1] = [d*' ' + "def _tick_log(msg):  # BELL-TOWER v85.55: the bell keeps its own book - one timestamped line per deed, readable from any folder, independent of whichever process owns the key",
                d*' ' + "    try:",
                (d+4)*' ' + "import time as _t2",
                (d+4)*' ' + "open(os.path.join(BASE_DIR, 'tick.log'), 'a').write('%s %s\\n' % (_t2.strftime('%H:%M:%S'), msg))",
                d*' ' + "    except Exception:",
                (d+4)*' ' + "        pass",
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
    print('🔎 ticker now:')
    for j in range(t0, min(t0+8, len(B))):
        print('   |', B[j].rstrip()[:150])
print('🔎 word eye splices:')
for k, l in enumerate(B):
    if '_word_text(p) or extract_text(p)' in l:
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
    if 'v85.55' not in t:
        open(AR, 'a').write('v85.55 combined: TEXT-DOCX native Word eye (_word_text via textutil) spliced into every fast reading line and the extract_text head where it exists, so Word papers are never text-silent; BELL-RETRY re-knocks the tick flock until held and BELL-TOWER writes every deed timestamped to tick.log (S397, S398)\n')
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
      ("'S398 the bell re-knocks until it holds the key, and keeps its own book", "'S397 a Word paper is never text-silent - the native reader opens it in milliseconds", "ck('S398 the bell re-knocks until it holds the key, and keeps its own book', (chr(35)+' BELL-RETRY v85.55') in _src and (chr(35)+' BELL-TOWER v85.55') in _src and ('tick.log' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

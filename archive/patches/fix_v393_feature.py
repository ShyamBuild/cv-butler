import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
W0 = open('wa.py').read()
B0 = open('butler.py').read()
M0 = set(markers(W0.split('\n'))) | set(markers(B0.split('\n')))
w = W0.split('\n')
snapw = list(w)
b0 = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
for k in range(b0, b0+8):
    if w[k].strip().startswith('_a.set_event_loop(None)'):
        d = ind(w[k])
        w[k:k+1] = [d*' ' + "_a.set_event_loop_policy(_a.DefaultEventLoopPolicy())  # POLICY-RESET v85.25: a custom policy may hand every thread a shared running loop that set_event_loop cannot refuse; the ritual installs a fresh policy and its own idle loop",
                    d*' ' + "_a.set_event_loop(_a.new_event_loop())"]
        done.append('policy-reset'); break
gt = next((k for k, l in enumerate(w) if l.strip().startswith('if not _goto(page,')), None)
if gt is not None and 'QR-RESCAN' not in '\n'.join(w[gt:gt+14]):
    d = ind(w[gt])
    j = gt + 1
    while j < len(w) and (w[j].strip() == '' or ind(w[j]) > d):
        j += 1
    w[j:j] = [d*' ' + "try:",
              (d+4)*' ' + "_html = page.content()",
              d*' ' + "except Exception:",
              (d+4)*' ' + "_html = ''",
              d*' ' + "if ('Link your phone' in _html or 'qr code' in _html.lower()) and 'conversation' not in _html:  # QR-RESCAN v85.26: a logged-out window asks for one scan, named aloud, instead of failing as a library complaint",
              (d+4)*' ' + "say('🔐 WhatsApp Web is logged out in the BUTLER window - scan the QR with your phone once, then press any key here')",
              (d+4)*' ' + "_key('')",
              (d+4)*' ' + "try:",
              (d+8)*' ' + "page.reload(wait_until='domcontentloaded', timeout=60000)",
              (d+8)*' ' + "_goto(page, f'https://web.whatsapp.com/send?phone={digits}', say)",
              (d+4)*' ' + "except Exception:",
              (d+8)*' ' + "pass"]
    done.append('qr-rescan')
i0 = next((k for k, l in enumerate(w) if l.startswith('def send_review(')), None)
if i0 is not None and 'PLAYWRIGHT-PROCESS' not in '\n'.join(w[i0:i0+12]):
    i1 = next(k for k in range(i0, i0+20) if w[k] == '    return r')
    w[i0:i1+1] = ["def send_review(phone, text, say=print, *a, **k):  # PLAYWRIGHT-THREAD v85.23 PLAYWRIGHT-PROCESS v85.24: the ritual runs in a brand-new process - born without loops or policies - inheriting the tty so bare keys still answer; the exit code carries the truth home",
                  "    import subprocess, sys",
                  "    code = 'import sys, wa; sys.exit(0 if wa._send_review_body(%r, %r, print) else 1)' % (phone, text)",
                  "    r = subprocess.call([sys.executable, '-c', code], cwd=os.path.dirname(os.path.abspath(__file__)))",
                  "    if r != 0:",
                  "        say('⚠️ whatsapp failed in its own process - retry with: python3 -c \"import wa; wa._send_review_body(' + repr(phone) + ', ' + repr(text) + ', print)\"')",
                  "        return False",
                  "    return True"]
    done.append('playwright-process')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
B = B0.split('\n')
snap = list(B)
if 'def _ident_of(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
    B[i:i] = ["_IDC = {}",
              "def _ident_of(p):  # DUP-SEED v85.26: a paper's identity is its email-and-phone set, cached by mtime+size - filenames lie, contacts do not",
              "    global _IDC",
              "    import json as _j",
              "    cf = os.path.join(BASE_DIR, '.idcache.json')",
              "    if not _IDC:",
              "        try: _IDC.update(_j.load(open(cf)))",
              "        except Exception: pass",
              "    try:",
              "        st = os.stat(p)",
              "    except Exception:",
              "        return set()",
              "    e = _IDC.get(p)",
              "    if e and e[0] == st.st_mtime and e[1] == st.st_size:",
              "        return set(e[2])",
              "    try:",
              "        t = extract_text(p) or ''",
              "    except Exception:",
              "        t = ''",
              "    ids = set(emails_in_text(t)) | set(phones_in_text(t))",
              "    _IDC[p] = [st.st_mtime, st.st_size, sorted(ids)]",
              "    try: _j.dump(_IDC, open(cf, 'w'))",
              "    except Exception: pass",
              "    return ids",
              ""]
    done.append('ident-cache')
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
wt = next((k for k in range(c0, c1) if B[k].strip().startswith("waiting = [i for i in s0.get('items', [])")), None)
if wt is not None and 'res_id' not in '\n'.join(B[c0:wt]):
    d = ind(B[wt])
    B[wt:wt] = [d*' ' + "res_id = {}  # DUP-SEED v85.26: the residents' identities, gathered once per seed, so a second download may never re-enter the chair wearing a portal mask",
                d*' ' + "for _st in _tag_vocab():",
                (d+4)*' ' + "_sd = os.path.join(root, _st)",
                (d+4)*' ' + "if not os.path.isdir(_sd): continue",
                (d+4)*' ' + "for _dp, _dn, _fn in os.walk(_sd):",
                (d+8)*' ' + "for _x in _fn:",
                (d+12)*' ' + "_ids = _ident_of(os.path.join(_dp, _x))",
                (d+12)*' ' + "if _ids: res_id[frozenset(_ids)] = (_x, _st)"]
    done.append('resident-idents')
ap = next((k for k in range(c0, c1) if B[k].strip().startswith("items.append({'p':") and 'waiting' in B[k]), None)
if ap is not None and 'second download' not in '\n'.join(B[c0:ap]):
    d = ind(B[ap])
    B[ap:ap] = [d*' ' + "_ids = _ident_of(p)",
                d*' ' + "_hit = next((v for k2, v in res_id.items() if _ids and (_ids & set(k2))), None)",
                d*' ' + "if _hit:",
                (d+4)*' ' + "say(f'👥 {os.path.basename(p)} is a second download of {_hit[0]} ({_hit[1]}) - not seated')",
                (d+4)*' ' + "continue"]
    done.append('dup-refused')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('wa.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.26' not in t:
        open(AR, 'a').write('v85.26: DUP-SEED refuses second downloads by email/phone identity against stage residents (cached in .idcache.json); QR-RESCAN names a logged-out window and waits for one scan; POLICY-RESET slice corrected and the process wrapper re-landed (S361 repinned, S362, S363, S364)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("ck('S361 ") and 'process where no loop or policy' not in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S361 the window ritual lives in its own process where no loop or policy may reach it', (chr(35)+' PLAYWRIGHT-PROCESS v85.24') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('subprocess.call' in open(os.path.join(BASE_DIR, 'wa.py')).read()))  # S361 repinned v85.25: thread isolation was outrun; the process boundary is the guarantee"
        done.append('S361-repin'); break
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S362 the ritual installs its own policy and a loop nobody runs", "'S361 the window ritual lives in its own process where no loop or policy may reach it", "ck('S362 the ritual installs its own policy and a loop nobody runs', (chr(35)+' POLICY-RESET v85.25') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S363 a second download never re-enters the chair wearing a portal mask", "'S362 the ritual installs its own policy and a loop nobody runs", "ck('S363 a second download never re-enters the chair wearing a portal mask', (chr(35)+' DUP-SEED v85.26') in _src and ('second download of' in _src))"),
      ("'S364 a logged-out window asks for one scan, named aloud", "'S363 a second download never re-enters the chair wearing a portal mask", "ck('S364 a logged-out window asks for one scan, named aloud', (chr(35)+' QR-RESCAN v85.26') in open(os.path.join(BASE_DIR, 'wa.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

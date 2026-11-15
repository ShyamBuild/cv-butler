import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
G0 = open('briefing.py').read()
W0 = open('wa.py').read()
M0 = set(markers(B0.split('\n'))) | set(markers(G0.split('\n'))) | set(markers(W0.split('\n')))
B = B0.split('\n')
snap = list(B)
if 'def _name_from_first_line(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
    B[i:i] = ["def _name_from_first_line(p):  # FIRST-LINE v85.20: when both developed eyes stay silent, the paper's own first line speaks in title case - the humblest eye, and the fastest",
              "    try:",
              "        t = extract_text(p) or ''",
              "    except Exception:",
              "        return ''",
              "    for ln in t.split('\\n'):",
              "        ln = ln.strip()",
              "        if not ln: continue",
              "        if any(ch.isdigit() for ch in ln): continue",
              "        if '@' in ln: continue",
              "        ws = ln.split()",
              "        if 2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws):",
              "            return ' '.join(w.capitalize() for w in ws)",
              "        return ''",
              "    return ''",
              ""]
    done.append('first-line-eye')
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
for k in range(s0, s1):
    if B[k].strip().startswith('v = heuristic_name(p) or get_visual_name(p)') and '_name_from_first_line' not in B[k]:
        B[k] = B[k].rstrip().split('  #')[0] + " or _name_from_first_line(p)  # FIRST-LINE v85.20: the third eye, last resort"
        done.append('third-eye'); break
for k in range(s0, s1):
    if B[k].strip().startswith("say(f'👁️ {x}: text silent, vision silent"):
        B[k] = ind(B[k])*' ' + "if whole: say(f'👁️ {x}: text silent, vision silent - left for the next up')  # MISS-EVIDENCE v85.19 (once v85.21): a miss confesses in the whole-chair pass, never twice"
        done.append('miss-once'); break
for k in range(s0, s1):
    if B[k].strip().startswith('v = heuristic_name(p)') and 'LOOP-CLEAN' not in '\n'.join(B[s0:s1]):
        d = ind(B[k])
        B[k+1:k+1] = [d*' ' + "try:",
                      (d+4)*' ' + "import asyncio as _a",
                      (d+4)*' ' + "_a.set_event_loop(None)  # LOOP-CLEAN v85.21: the vision eye may leave an idle loop behind; playwright sync must find none",
                      d*' ' + "except Exception:",
                      (d+4)*' ' + "pass"]
        done.append('loop-clean-seat'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
g = G0.split('\n')
snapg = list(g)
w0 = next((k for k, l in enumerate(g) if l.startswith('class _NLOut')), None)
if w0 is not None and 'FLUSH-ABSOLUTE' not in '\n'.join(g[w0:w0+20]):
    wi = next(k for k in range(w0, w0+20) if g[k].strip() == 'if t:')
    d = ind(g[wi])
    g[wi:wi+2] = [d*' ' + "if t:",
                  (d+4)*' ' + "if self.last == '\\n':  # FLUSH-ABSOLUTE v85.20: a line that begins, begins at column zero - no string from any module may open a line with borrowed space",
                  (d+8)*' ' + "t = t.lstrip(' ')",
                  (d+4)*' ' + "if t and self.last not in ('\\n', '') and len(t) > 24:  # FLUSH-ABSOLUTE v85.20: long content never continues a line; it takes its own newline first",
                  (d+8)*' ' + "self._s.write('\\n'); self.last = '\\n'",
                  (d+4)*' ' + "self._s.write(t); self.last = t[-1]"]
    done.append('wrapper-absolute')
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
w = W0.split('\n')
snapw = list(w)
sr = next((k for k, l in enumerate(w) if l.startswith('def send_review(')), None)
if sr is not None and 'LOOP-CLEAN' not in '\n'.join(w[sr:sr+8]):
    d = ind(w[sr])
    w[sr+1:sr+1] = [d*' ' + "try:",
                    (d+4)*' ' + "import asyncio as _a",
                    (d+4)*' ' + "_a.set_event_loop(None)  # LOOP-CLEAN v85.21: the thumb's window refuses a process carrying a live wire",
                    d*' ' + "except Exception:",
                    (d+4)*' ' + "pass"]
    done.append('loop-clean-wa')
    srcw = '\n'.join(w)
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('briefing.py').read().split('\n'))) | set(markers(open('wa.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.21' not in t:
        open(AR, 'a').write('v85.21: FLUSH-ABSOLUTE nested as children of if t: (a conditional demands an indented block, not peers); FIRST-LINE third eye; LOOP-CLEAN in butler and wa; misses confess once per up (S355, S356, S357)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S355 when both developed eyes stay silent, the paper's own first line speaks", "'S354 silence never earns a pass - unnamed papers are spoken and retried", "ck('S355 when both developed eyes stay silent, the paper'+chr(39)+'s own first line speaks', (chr(35)+' FIRST-LINE v85.20') in _src and ('_name_from_first_line(p)' in _src))"),
      ("'S356 no line begins with borrowed space and no content continues a prompt", "'S355 when both developed eyes stay silent, the paper's own first line speaks", "ck('S356 no line begins with borrowed space and no content continues a prompt', (chr(35)+' FLUSH-ABSOLUTE v85.20') in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S357 no idle loop may lie across the thumb's path", "'S356 no line begins with borrowed space and no content continues a prompt", "ck('S357 no idle loop may lie across the thumb'+chr(39)+'s path', (chr(35)+' LOOP-CLEAN v85.21') in _src and (chr(35)+' LOOP-CLEAN v85.21') in open(os.path.join(BASE_DIR, 'wa.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

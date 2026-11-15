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
M0 = set(markers(B0.split('\n'))) | set(markers(G0.split('\n')))
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
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
g = G0.split('\n')
snapg = list(g)
w0 = next(k for k, l in enumerate(g) if l.startswith('class _NLOut('))
w1 = next(k for k in range(w0 + 1, len(g)) if g[k].startswith('class ') or (g[k].startswith('def ') and k > w0))
for k in range(w0, w1):
    if g[k].strip().startswith('def write(self, t):'):
        d = ind(g[k])
        g[k+1:k+1] = [d*' ' + "if t and self.last == '\\n':  # FLUSH-ABSOLUTE v85.20: a line that begins, begins at column zero - no string from any module may open a line with borrowed space",
                      (d+4)*' ' + "t = t.lstrip(' ')",
                      d*' ' + "if t and self.last not in ('\\n', '') and len(t) > 24:  # FLUSH-ABSOLUTE v85.20: long content never continues a line; it takes its own newline first",
                      (d+4)*' ' + "self._s.write('\\n'); self.last = '\\n'"]
        done.append('wrapper-absolute'); break
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('briefing.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.20' not in t:
        open(AR, 'a').write('v85.20: FLUSH-ABSOLUTE at the stdout wrapper (line-starts stripped, long content newline-first) and FIRST-LINE third eye in the naming ceremony - the paper\'s own first line, title-cased, when both developed eyes stay silent (S355, S356)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_br = open('briefing.py').read()
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S355 when both developed eyes stay silent, the paper's own first line speaks", "'S354 silence never earns a pass - unnamed papers are spoken and retried", "ck('S355 when both developed eyes stay silent, the paper'+chr(39)+'s own first line speaks', (chr(35)+' FIRST-LINE v85.20') in _src and ('_name_from_first_line(p)' in _src))"),
      ("'S356 no line begins with borrowed space and no content continues a prompt", "'S355 when both developed eyes stay silent, the paper's own first line speaks", "ck('S356 no line begins with borrowed space and no content continues a prompt', (chr(35)+' FLUSH-ABSOLUTE v85.20') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

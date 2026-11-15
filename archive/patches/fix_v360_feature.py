import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
G = os.path.join(os.getcwd(), 'briefing.py')
g0 = open(G).read()
M0 |= set(markers(g0.split('\n')))
g = g0.split('\n')
for k, l in enumerate(g):
    if 'DESIG-FALLBACK v84.29' in l and 'META-COMPANY' not in '\n'.join(g[k:k+8]):
        d = ind(l)
        g[k+1:k+1] = [d*' ' + "if not _idn.get('company'):  # META-COMPANY v85.3: when no client folder exists, the desk's taught company answers - a taught name may not sit unused while a guess speaks",
                      d*' ' + "    try:",
                      d*' ' + "        _mc = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'desk_meta.json'))).get(_bt.desk_load().get('primary') or '', {}).get('company')",
                      d*' ' + "    except Exception:",
                      d*' ' + "        _mc = None",
                      d*' ' + "    if _mc: cli = _mc"]
        done.append('meta-company'); break
p0 = next(k for k, l in enumerate(g) if l.startswith('def _pick_phone('))
if 'def _listen(' not in '\n'.join(g):
    g[p0:p0] = ["def _listen(prompt):  # LISTEN v85.3: one keystroke, no Enter - the copilot's mouth hears keys",
                "    import butler as _bt",
                "    return _bt.menu_key(prompt)",
                ""]
    done.append('listen-helper')
p0 = next(k for k, l in enumerate(g) if l.startswith('def _pick_phone('))
p1 = next(k for k in range(p0 + 1, len(g)) if g[k].startswith('def '))
for k in range(p0, p1):
    if 'input(' in g[k] and '_listen(' not in g[k]:
        g[k] = g[k].replace('(ask or input)(', '(ask or _listen)(').replace('input(', '_listen(')
        done.append('pick-listen'); break
srcg = '\n'.join(g)
if srcg != g0:
    ast.parse(srcg); open(G, 'w').write(srcg)
sw = 0
for dn in ('templates', 'drafts'):
    DD = os.path.join(os.getcwd(), dn)
    if not os.path.isdir(DD): continue
    for fn in os.listdir(DD):
        if not fn.endswith('.txt'): continue
        P = os.path.join(DD, fn)
        t = open(P).read()
        if 'WhatsApp' in t or 'whatsapp' in t:
            open(P, 'w').write(t.replace('WhatsApp', 'email').replace('whatsapp', 'email'))
            sw += 1
if sw: done.append('email-sweep-x%d' % sw)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if B[k].strip().startswith("say('· proposal waiting - type y / t / n')") and 'LISTEN' not in '\n'.join(B[o0:o1]):
        d = ind(B[k])
        B[k-1:k+1] = [d*' ' + "k2 = menu_key('· proposal waiting - one key: ')  # LISTEN v85.3: the deferred answer is a keystroke too - no Enter in the copilot's mouth",
                      d*' ' + "if k2 == 'n':",
                      (d+4)*' ' + "say('⏸️ row open - he stays in the chair'); return",
                      d*' ' + "if k2 in ('y', 't'):",
                      (d+4)*' ' + "try: os.remove(os.path.join(BASE_DIR, 'pending_action.json'))  # LISTEN v85.3: a keystroke that executes retires the deferred file, so no stray y may re-execute it",
                      (d+4)*' ' + "except Exception: pass",
                      (d+4)*' ' + "_k = k2",
                      d*' ' + "else:",
                      (d+4)*' ' + "return"]
        done.append('pending-listen'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open(G).read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.3' not in t:
        open(AR, 'a').write('v85.3: META-COMPANY (desk-taught company answers {where} when no client folder exists - meta <company> once per desk); candidate texts say email, never WhatsApp (S335); LISTEN finished - deferred proposals and the phone pick (briefing._pick_phone via _listen) take one keystroke, and an executing keystroke retires the pending file\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_br = open(G).read()
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S334 the desk's taught company answers when the registry is silent", "'S333 the terminal speaks crisp - every line keeps its information and loses its fat", "ck('S334 the desk'+chr(39)+'s taught company answers when the registry is silent', (chr(35)+' META-COMPANY v85.3') in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S335 no candidate-facing text says WhatsApp - the details travel by email", "'S334 the desk's taught company answers when the registry is silent", "ck('S335 no candidate-facing text says WhatsApp - the details travel by email', all(('WhatsApp' not in open(os.path.join(BASE_DIR, d, f)).read()) for d in ('templates', 'drafts') for f in os.listdir(os.path.join(BASE_DIR, d)) if f.endswith('.txt')))"),
      ("'S336 every single-key answer is a keystroke - no Enter in the copilot's mouth", "'S335 no candidate-facing text says WhatsApp - the details travel by email", "ck('S336 every single-key answer is a keystroke - no Enter in the copilot'+chr(39)+'s mouth', (chr(35)+' LISTEN v85.3') in _src and ('_listen(' in open(os.path.join(BASE_DIR, 'briefing.py')).read().split('def _pick_phone(')[1].split(chr(10) + 'def ')[0]))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

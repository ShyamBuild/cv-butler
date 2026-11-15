import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
G = os.path.join(os.getcwd(), 'briefing.py')
g0 = open(G).read()
M0 = set(markers(g0.split('\n'))) | set(markers(open('butler.py').read().split('\n')))
g = g0.split('\n')
s0 = next((k for k, l in enumerate(g) if l.startswith('def _smart_input(')), None)
if s0 is not None and 'ALWAYS-RAW' not in g[s0]:
    s1 = next(k for k in range(s0 + 1, len(g)) if g[k].startswith('def '))
    g[s0:s1] = ["def _smart_input(prompt):  # LISTEN-REPL v85.4  # ALWAYS-RAW v85.6: the REPL always hears keys - a digit or y/t/n lands on the press; a word accumulates with live echo and backspace; Enter terminates words only",
                "    import sys, termios, tty",
                "    sys.stdout.write(prompt); sys.stdout.flush()",
                "    try:",
                "        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)",
                "        tty.setraw(fd)",
                "        try:",
                "            buf = ''",
                "            while True:",
                "                c = sys.stdin.read(1)",
                "                if c == '\\x03':",
                "                    sys.stdout.write('^C\\n'); sys.stdout.flush(); raise KeyboardInterrupt",
                "                if c in ('\\r', '\\n'):",
                "                    sys.stdout.write('\\n'); sys.stdout.flush()",
                "                    return buf.strip()",
                "                if c == '\\x7f':",
                "                    if buf:",
                "                        buf = buf[:-1]; sys.stdout.write('\\b \b'); sys.stdout.flush()",
                "                    continue",
                "                if not buf and c in '1234567ytn':",
                "                    sys.stdout.write(c + '\\n'); sys.stdout.flush()",
                "                    return c",
                "                buf += c",
                "                sys.stdout.write(c); sys.stdout.flush()",
                "        finally:",
                "            termios.tcsetattr(fd, termios.TCSADRAIN, old)",
                "    except KeyboardInterrupt:",
                "        raise",
                "    except Exception:",
                "        return input('')",
                ""]
    done.append('always-raw')
srcg = '\n'.join(g)
if srcg != g0:
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
snap = list(B)
w0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_wa_text('))
w1 = next(k for k in range(w0 + 1, len(B)) if B[k].startswith('def '))
r0 = next((k for k in range(w0, w1) if B[k].strip().startswith("if kind == 'refer':") and 'SCENARIO-REFER' in B[k]), None)
if r0 is not None and ind(B[r0]) > 4:
    r1 = r0
    while r1 + 1 < w1 and (ind(B[r1+1]) > ind(B[r0]) or B[r1+1].strip() == ''):
        r1 += 1
    del B[r0:r1+1]
    done.append('refer-lifted')
t3 = next((k for k, l in enumerate(B) if l.strip() == 'if t3: return t3'), None)
if t3 is not None and not any(B[j].strip().startswith("if kind == 'refer':") for j in range(t3, min(t3+8, len(B)))):
    B[t3+1:t3+1] = ["    if kind == 'refer':  # SCENARIO-REFER v85.4 (dedented v85.8): the refer branch stands beside the cv branch at column four, never buried inside it",
                    "        try:",
                    "            _rp = os.path.join(DRAFTS_DIR, 'refer.txt')",
                    "            if os.path.exists(_rp): return open(_rp).read().strip().format_map(_draft_fields(name, _pos_of(p, _pl_root()), p))",
                    "        except Exception:",
                    "            pass"]
    done.append('refer-dedent')
print('🔎 _chair_wa_text region after surgery:')
w0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_wa_text('))
for l in B[w0:w0+14]:
    print('   |', l)
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
    if 'v85.8' not in t:
        open(AR, 'a').write('v85.8: the refer branch dedented to column four beside its cv sibling (an insert copied its anchor indent and landed inside the wrong body); always-raw listener returned whole with both markers hashed; S341 pins the refer branch column so no scenario may bury another again\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S340 no state may downgrade the keyboard - the REPL always hears keys", "'S339 no guard may pin a read-call - prompts are law, readers are manners", "ck('S340 no state may downgrade the keyboard - the REPL always hears keys', (chr(35)+' ALWAYS-RAW v85.6') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('_seated' not in open(os.path.join(BASE_DIR, 'briefing.py')).read().split('def _smart_input(')[1].split(chr(10) + 'def ')[0]))"),
      ("'S341 a scenario branch stands at its own column, never inside its sibling", "'S340 no state may downgrade the keyboard - the REPL always hears keys", "ck('S341 a scenario branch stands at its own column, never inside its sibling', _src.count(chr(10) + \"    if kind == 'refer':\") == 1)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
w0 = next(k for k, l in enumerate(B) if l.startswith('def confirm_wait('))
w1 = next(k for k in range(w0 + 1, len(B)) if B[k].startswith('def '))
marks = set()
for l in B[w0:w1]:
    marks.update(re.findall(r'# ([A-Z0-9-]+ v[0-9.]+)', l))
extra = [m for m in marks if not m.startswith('KEY-CONFIRM')]
if extra:
    print('⛔ mw.sh equivalent: confirm_wait carries witnesses I have not read -', sorted(extra))
    raise SystemExit('paste sed -n \'%d,%dp\' ~/CV_Tool/butler.py before this lap may replace it' % (w0 + 1, w1))
print('🔎 mw.sh equivalent: confirm_wait region carries only', sorted(marks) or 'nothing', '- replace is witness-safe')
if 'INLINE-ECHO' not in '\n'.join(B[w0:w1]):
    d = ind(B[w0])
    B[w0:w1] = [d*' ' + "def confirm_wait(say=print):  # KEY-CONFIRM v84.6: the answer is a keystroke, not a line - like the WhatsApp menu (INLINE-ECHO v84.45: the key you press appears on the proposal's own line)",
                d*' ' + "    import sys, termios, tty",
                d*' ' + "    try:",
                d*' ' + "        fd = sys.stdin.fileno()",
                d*' ' + "        old = termios.tcgetattr(fd)",
                d*' ' + "        try:",
                d*' ' + "            tty.setraw(fd)",
                d*' ' + "            k = sys.stdin.read(1)",
                d*' ' + "        finally:",
                d*' ' + "            termios.tcsetattr(fd, termios.TCSADRAIN, old)",
                d*' ' + "    except Exception:",
                d*' ' + "        return None",
                d*' ' + "    if k in ('y', 'n', 'Y', 'N'):",
                d*' ' + "        sys.stdout.write(k.lower() + '\\n'); sys.stdout.flush()  # INLINE-ECHO v84.45: question and answer on one line, the way the hand acted",
                d*' ' + "        return k.lower()",
                d*' ' + "    sys.stdout.write('\\n'); sys.stdout.flush()",
                d*' ' + "    return k if k not in ('\\r', '\\n') else None",
                ""]
    done.append('confirm-inline')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.45' not in t:
        open(AR, 'a').write('v84.45: confirm_wait echoes the pressed key onto the proposal line (raw mode had swallowed it); Enter still defers to a typed y/n; region replaced only after its marker count came back clean\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S315 the keystroke answers on its own question's line", "'S314 a nudge changes no tag and moves nothing", "ck('S315 the keystroke answers on its own question'+chr(39)+'s line', (chr(35)+' INLINE-ECHO v84.45') in _src and ('sys.stdout.write(k.lower()' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

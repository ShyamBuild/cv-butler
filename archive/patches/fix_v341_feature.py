import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
def parse_ok(X):
    try:
        ast.parse('\n'.join(X)); return True
    except Exception:
        return False
B = open('butler.py').read().split('\n')
snap = list(B)
m0 = next(k for k, l in enumerate(B) if l.startswith('def menu_key('))
m1 = next(k for k in range(m0 + 1, len(B)) if B[k].startswith('def _preview_open('))
B[m0:m1] = ["def menu_key(prompt='', allowed=('y', 't', 'n')):  # ONE-INPUT v84.47 (ASK-LINE v84.49): the statement ends in its own line; the question ends in a visible cue; the key signs it; Enter re-asks once; Ctrl+C cancels like everywhere else",
            "    import sys, termios, tty",
            "    for attempt in (0, 1):",
            "        sys.stdout.write(prompt if attempt == 0 else '   one key, master: y / t / n › '); sys.stdout.flush()",
            "        try:",
            "            fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)",
            "            try:",
            "                tty.setraw(fd); k = sys.stdin.read(1)",
            "            finally:",
            "                termios.tcsetattr(fd, termios.TCSADRAIN, old)",
            "        except Exception:",
            "            return (input() or '').strip().lower()",
            "        if k == '\\x03':",
            "            sys.stdout.write('^C\\n'); sys.stdout.flush(); return 'n'",
            "        if k in ('\\r', '\\n'):",
            "            sys.stdout.write('\\n'); sys.stdout.flush()",
            "            if attempt == 0: continue",
            "            return ''",
            "        sys.stdout.write(k + '\\n'); sys.stdout.flush()",
            "        return k.strip().lower()",
            "    return ''",
            ""]
if parse_ok(B): done.append('menu-key-askline')
else: B = list(snap); done.append('revert:menu-key-askline')
snap = list(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if "[n] cancel', end='')" in B[k]:
        d = ind(B[k])
        B[k:k+2] = [d*' ' + "say(f\"🤖 Proposal: {cur['name']} → \" + _tagpart + f\" ({outcome})\" + (f' · WhatsApp {draft} draft will open, unsent' if draft else ' · no message - this one stays in the house'))  # ASK-LINE v84.49: the statement ends in its own line",
                    d*' ' + "k = menu_key('   y = do + WhatsApp draft · t = do only · n = cancel › ')  # ASK-LINE v84.49: the question waits at a visible cue and the key signs it"]
        done.append('outcome-twoline'); break
if not parse_ok(B): B = list(snap); done.append('revert:outcome-twoline')
snap = list(B)
t0 = next(k for k, l in enumerate(B) if l.startswith('def _tag_apply_one('))
t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def '))
for k in range(t0, t1):
    if B[k].strip().startswith("say(txt + ' · y / n', end='')"):
        d = ind(B[k])
        B[k] = d*' ' + "say(txt)  # ASK-LINE v84.49: statement first, question second"
        if B[k+1].strip() == 'k = menu_key()':
            B[k+1] = d*' ' + "k = menu_key('   y = yes · t = yes, no draft · n = cancel › ')  # ASK-LINE v84.49"
        done.append('tagvoice-twoline'); break
if not parse_ok(B): B = list(snap); done.append('revert:tagvoice-twoline')
src = '\n'.join(B); open('butler.py', 'w').write(src)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.49' not in t:
        open(AR, 'a').write('v84.49: ASK-LINE - every proposal is two beats (statement line, cue line ending in › where the cursor waits); the key signs the cue line; Enter re-asks once; Ctrl+C cancels plainly; no question may ever listen in silence again\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S320 no question may listen in silence - the cue line waits visibly and Ctrl+C cancels", "'S319 the unknown-outcome confession counts all seven doors", "ck('S320 no question may listen in silence - the cue line waits visibly and Ctrl+C cancels', (chr(35)+' ASK-LINE v84.49') in _src and ('x03' in _src) and ('one key, master' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

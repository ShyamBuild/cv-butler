import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'TAG-SANITIZE' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _tags_of('))
    i1 = next(k for k in range(i + 1, len(B)) if B[k].strip().startswith('for t in (arr or []):'))
    i2 = next(k for k in range(i1, len(B)) if B[k].strip() == 'return out')
    B[i1:i2] = ["    for t in (arr or []):",
                "        if isinstance(t, bytes): t = t.decode('utf-8', 'ignore')",
                "        t = str(t).split(chr(10))[0].strip()  # TAG-SANITIZE v84.6: a tag is one line; stray newlines and bare digits are noise, not names",
                "        if t and not t.isdigit(): out.append(t)"]
    done.append('tag-sanitize')
    src = '\n'.join(B)
if 'def confirm_wait(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def action_pending('))
    B[i:i] = ["def confirm_wait(say=print):  # KEY-CONFIRM v84.6: the answer is a keystroke, not a line - like the WhatsApp menu",
              "    import sys, tty, termios",
              "    try:",
              "        if not sys.stdin.isatty(): return None",
              "        fd = sys.stdin.fileno()",
              "        old = termios.tcgetattr(fd)",
              "        try:",
              "            tty.setraw(fd)",
              "            ch = sys.stdin.read(1)",
              "        finally:",
              "            termios.tcsetattr(fd, termios.TCSAFLUSH, old)",
              "        print()",
              "        return ch.lower()",
              "    except Exception:",
              "        return None",
              ""]
    done.append('key-confirm')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("try: _j.dump({'p': p, 'tag': tag, 'on': on, 'move_to'") and 'confirm_wait' not in '\n'.join(B[k:k+4]):
        d = ind(l)
        B.insert(k+2, d*' ' + "k = confirm_wait(say)")
        B.insert(k+3, d*' ' + "if k in ('y',): action_execute(say)")
        B.insert(k+4, d*' ' + "elif k in ('n',): action_cancel(say)")
        B.insert(k+5, d*' ' + "elif k is not None: say('proposal left waiting - answer y or n on the next line')")
        done.append('proposal-keywait'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S242 a tag is one line - noise is dropped at the door", "'S241 a transition shows now and after before it asks", "ck('S242 a tag is one line - noise is dropped at the door', (chr(35)+' TAG-SANITIZE v84.6') in _src)"),
      ("'S243 a proposal is answered by a keystroke, like the WhatsApp menu", "'S242 a tag is one line - noise is dropped at the door", "ck('S243 a proposal is answered by a keystroke, like the WhatsApp menu', (chr(35)+' KEY-CONFIRM v84.6') in _src and ('def confirm_wait(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def one_key(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def confirm_wait('))
    B[i:i] = ["def one_key(prompt):  # ONE-KEY v84.46: where a single letter is the whole answer, the letter alone suffices - echoed on its own line's end",
              "    import sys, termios, tty",
              "    sys.stdout.write(prompt); sys.stdout.flush()",
              "    try:",
              "        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)",
              "        try:",
              "            tty.setraw(fd); k = sys.stdin.read(1)",
              "        finally:",
              "            termios.tcsetattr(fd, termios.TCSADRAIN, old)",
              "    except Exception:",
              "        return (input() or '').strip().lower()",
              "    if k in ('\\r', '\\n'):",
              "        sys.stdout.write('\\n'); sys.stdout.flush(); return ''",
              "    sys.stdout.write(k + '\\n'); sys.stdout.flush()",
              "    return k.strip().lower()",
              "def _preview_open(p, say=print):  # PREVIEW v84.46: the seated paper opens in Preview behind your eyes; already-open is fine; the machine never closes what you opened",
              "    if not (p or '').lower().endswith('.pdf'): return",
              "    try:",
              "        import subprocess",
              "        out = subprocess.run(['osascript', '-e', 'tell application \"Preview\" to get name of windows'], capture_output=True, text=True, timeout=5).stdout or ''",
              "        if os.path.basename(p) in out: return",
              "        subprocess.Popen(['open', '-g', '-a', 'Preview', p])",
              "    except Exception:",
              "        pass",
              ""]
    done.append('one-key-and-preview')
    src = '\n'.join(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if '_preview_open(p, say)' not in '\n'.join(B[u0:u1]):
    for k in range(u0, u1):
        if B[k].strip().startswith('say(f"📞 UP:'):
            B.insert(k+1, ind(B[k])*' ' + "_preview_open(p, say)")
            done.append('preview-hook'); break
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "input('📱 draft WhatsApp? [y] yes · [n] skip (tag only): '" in l:
        B[k] = ind(l)*' ' + "_r = one_key('📱 draft WhatsApp? [y] yes · [n] skip (tag only): ')  # ONE-KEY v84.46"
        done.append('skipwa-onekey'); break
for k, l in enumerate(B):
    if "input('📱 draft WhatsApp? [y] yes · [n] skip (no text): '" in l:
        B[k] = ind(l)*' ' + "_r0 = one_key('📱 draft WhatsApp? [y] yes · [n] skip (no text): ')  # ONE-KEY v84.46"
        done.append('nudge-onekey'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
srcw = '\n'.join(w)
if 'def _key(' not in srcw:
    i = next(k for k, l in enumerate(w) if l.startswith('def send_review('))
    w[i:i] = ["def _key(prompt):  # ONE-KEY v84.46: the menu answers to the keystroke alone; Enter still means take your time",
              "    import sys, termios, tty",
              "    sys.stdout.write(prompt); sys.stdout.flush()",
              "    try:",
              "        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)",
              "        try:",
              "            tty.setraw(fd); k = sys.stdin.read(1)",
              "        finally:",
              "            termios.tcsetattr(fd, termios.TCSADRAIN, old)",
              "    except Exception:",
              "        return (input() or '').strip().lower()",
              "    if k in ('\\r', '\\n'):",
              "        sys.stdout.write('\\n'); sys.stdout.flush(); return ''",
              "    sys.stdout.write(k + '\\n'); sys.stdout.flush()",
              "    return k.strip().lower()",
              ""]
    done.append('wa-key-def')
    srcw = '\n'.join(w)
for k, l in enumerate(w):
    if '(ask or input)(' in l and '[s] I clicked send myself' in l:
        d = ind(l)
        w[k:k+1] = [d*' ' + "_pm = '   [s] I clicked send myself · [x] discard & clear · [q] leave in field & close · [Enter] keep waiting: '",
                    d*' ' + "c = (ask(_pm).strip().lower() if ask else _key(_pm))  # ONE-KEY v84.46"]
        done.append('wa-menu-onekey'); break
srcw = '\n'.join(w)
if srcw != open(W).read():
    ast.parse(srcw); open(W, 'w').write(srcw)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.46' not in t:
        open(AR, 'a').write('v84.46: up opens the seated PDF in Preview (open -g, only if no Preview window bears its name, never closes); one_key/_key make every single-letter door answer to the keystroke alone (skip-wa, nudge, wa menu)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S316 the seated paper opens in Preview, behind your eyes, never closed by the machine", "'S315 the keystroke answers on its own question's line", "ck('S316 the seated paper opens in Preview, behind your eyes, never closed by the machine', (chr(35)+' PREVIEW v84.46') in _src and ('def _preview_open(' in _src) and (\"'-g', '-a', 'Preview'\" in _src))"),
      ("'S317 every single-letter door answers to the keystroke alone", "'S316 the seated paper opens in Preview, behind your eyes, never closed by the machine", "ck('S317 every single-letter door answers to the keystroke alone', (chr(35)+' ONE-KEY v84.46') in _src and ('def one_key(' in _src) and (chr(35)+' ONE-KEY v84.46') in open(os.path.join(BASE_DIR, 'wa.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

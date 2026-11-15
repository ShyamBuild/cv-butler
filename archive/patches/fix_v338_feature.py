import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def menu_key(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def confirm_wait('))
    B[i:i] = ["def menu_key(prompt='', allowed=('y', 't', 'n')):  # ONE-INPUT v84.47: one keystroke decides the deed and the draft - echoed on the question's own line",
              "    import sys, termios, tty",
              "    if prompt: sys.stdout.write(prompt); sys.stdout.flush()",
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
    done.append('menu-key-and-preview')
    src = '\n'.join(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if '_preview_open(p, say)' not in '\n'.join(B[u0:u1]):
    for k in range(u0, u1):
        if B[k].strip().startswith('say(f"📞 UP:'):
            B.insert(k+1, ind(B[k])*' ' + "_preview_open(p, say)")
            done.append('preview-hook'); break
    src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if B[k].strip().startswith("say(f\"🤖 Proposal: {cur['name']} → \" + _tagpart") and 'end=' not in B[k]:
        d = ind(B[k])
        B[k] = d*' ' + "say(f\"🤖 Proposal: {cur['name']} → \" + _tagpart + f\" ({outcome})\" + (f' · WhatsApp {draft} draft will open, unsent' if draft else ' · no message - this one stays in the house') + ' · [y] do + WhatsApp draft · [t] do, no WhatsApp · [n] cancel', end='')  # ONE-INPUT v84.47: the menu and the echo share the proposal's line"
        done.append('proposal-menu'); break
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
kc = next(k for k in range(o0, o1) if B[k].strip() == 'k = confirm_wait(say)')
pw = next(k for k in range(kc, o1) if B[k].strip().startswith("say('· proposal waiting"))
pr = next(k for k in range(pw, o1) if B[k].strip() == 'return')
d = ind(B[kc])
B[kc:pr+1] = [d*' ' + "k = menu_key()  # ONE-INPUT v84.47: one keystroke decides deed and draft",
              d*' ' + "if k == 'n':",
              (d+4)*' ' + "say('· row left open - he stays in the chair'); return",
              d*' ' + "if k not in ('y', 't'):  # PROPOSE-WAIT v84.15: Enter or silence leaves a typed answer pending",
              (d+4)*' ' + "import json as _j2",
              (d+4)*' ' + "try: _j2.dump({'p': p, 'tag': tag, 'on': True, 'move_to': True, 'ts': int(time.time())}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))",
              (d+4)*' ' + "except Exception: pass",
              (d+4)*' ' + "say('')",
              (d+4)*' ' + "say('· proposal waiting - type y or n on the next line'); return",
              d*' ' + "_k = k"]
done.append('confirm-menu')
src = '\n'.join(B)
sw0 = next(k for k in range(o0, o1) if B[k].strip() == "_r = ''")
sw1 = next(k for k in range(sw0, o1) if B[k].strip().startswith('else: wa.send_review(ph, _chair_wa_text('))
d = ind(B[sw0])
B[sw0:sw1+1] = [d*' ' + "if _k == 't': say('🏷️ tagged only - WhatsApp skipped')  # ONE-INPUT v84.47: the second prompt is gone; the proposal's t already said it",
                d*' ' + "else: wa.send_review(ph, _chair_wa_text(draft, p, cur['name']), say)"]
done.append('skipwa-merged')
src = '\n'.join(B)
n0 = next(k for k in range(o0, o1) if B[k].strip() == "_r0 = ''")
n1 = next(k for k in range(n0, o1) if B[k].strip().startswith("if _r0 != 'n':"))
d = ind(B[n0])
B[n0:n1+1] = [d*' ' + "if _k != 't':  # ONE-INPUT v84.47: the nudge's draft decision lives in the same keystroke"]
done.append('nudge-merged')
src = '\n'.join(B)
t0 = next(k for k, l in enumerate(B) if l.startswith('def _tag_apply_one('))
t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def '))
for k in range(t0, t1):
    if B[k].strip() == 'k = confirm_wait(say)':
        B[k] = ind(B[k])*' ' + "k = menu_key()"
        done.append('tagvoice-menu'); break
for k in range(t0, t1):
    if B[k].strip().startswith("if k == 'y':") and 'menu' not in B[k]:
        B[k] = ind(B[k])*' ' + "if k in ('y', 't'):"
        done.append('tagvoice-t'); break
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
    if 'v84.47' not in t:
        open(AR, 'a').write('v84.47: ONE-INPUT - the proposal menu [y] do+draft / [t] do only / [n] cancel is the only confirmation; the second draft prompt is deleted; echo lands on the proposal line; Preview auto-open and wa one-key re-applied with whole-block slices\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S316 the seated paper opens in Preview, behind your eyes, never closed by the machine", "'S315 the keystroke answers on its own question's line", "ck('S316 the seated paper opens in Preview, behind your eyes, never closed by the machine', (chr(35)+' PREVIEW v84.46') in _src and ('def _preview_open(' in _src))"),
      ("'S317 every single-letter door answers to the keystroke alone", "'S316 the seated paper opens in Preview, behind your eyes, never closed by the machine", "ck('S317 every single-letter door answers to the keystroke alone', (chr(35)+' ONE-KEY v84.46') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('def menu_key(' in _src))"),
      ("'S318 one keystroke decides the deed and the draft - no second prompt", "'S317 every single-letter door answers to the keystroke alone", "ck('S318 one keystroke decides the deed and the draft - no second prompt', (chr(35)+' ONE-INPUT v84.47') in _src and ('draft WhatsApp? [y] yes' not in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

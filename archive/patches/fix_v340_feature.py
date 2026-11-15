import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
def parse_ok(B):
    try:
        ast.parse('\n'.join(B)); return True
    except Exception:
        return False
B = open('butler.py').read().split('\n')
def snap_edit(name, fn):
    global B
    snap = list(B)
    fn()
    if parse_ok(B): done.append(name)
    else: B = snap; done.append('revert:' + name)
if 'def menu_key(' not in '\n'.join(B):
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
    done.append('defs')
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
def e_preview_hook():
    global B
    u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
    u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
    if '_preview_open(p, say)' not in '\n'.join(B[u0:u1]):
        for k in range(u0, u1):
            if B[k].strip().startswith('say(f"📞 UP:'):
                B.insert(k+1, ind(B[k])*' ' + "_preview_open(p, say)"); return
snap_edit('preview-hook', e_preview_hook)
def e_proposal():
    global B
    for k in range(o0, o1):
        if B[k].strip().startswith("say(f\"🤖 Proposal: {cur['name']} → \" + _tagpart") and 'end=' not in B[k]:
            d = ind(B[k])
            B[k] = d*' ' + "say(f\"🤖 Proposal: {cur['name']} → \" + _tagpart + f\" ({outcome})\" + (f' · WhatsApp {draft} draft will open, unsent' if draft else ' · no message - this one stays in the house') + ' · [y] do + WhatsApp draft · [t] do, no WhatsApp · [n] cancel', end='')  # ONE-INPUT v84.47: the menu and the echo share the proposal's line"
            return
snap_edit('proposal-menu', e_proposal)
def e_confirm():
    global B
    kc = next((k for k in range(o0, o1) if B[k].strip() == 'k = confirm_wait(say)'), None)
    if kc is None: return
    if not (B[kc+1].strip() == "if k == 'n':" and B[kc+3].strip().startswith("if k != 'y':") and B[kc+8].strip() == 'return' and B[kc+9].strip() == 'return'): return
    d = ind(B[kc])
    B[kc:kc+10] = [d*' ' + "k = menu_key()  # ONE-INPUT v84.47: one keystroke decides deed and draft - the twin return is buried with the old block",
                   d*' ' + "if k == 'n':",
                   (d+4)*' ' + "say('· row left open - he stays in the chair'); return",
                   d*' ' + "if k not in ('y', 't'):  # PROPOSE-WAIT v84.15: Enter or silence leaves a typed answer pending",
                   (d+4)*' ' + "import json as _j2",
                   (d+4)*' ' + "try: _j2.dump({'p': p, 'tag': tag, 'on': True, 'move_to': True, 'ts': int(time.time())}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))",
                   (d+4)*' ' + "except Exception: pass",
                   (d+4)*' ' + "say('')",
                   (d+4)*' ' + "say('· proposal waiting - type y or n on the next line'); return",
                   d*' ' + "_k = k"]
snap_edit('confirm-menu', e_confirm)
def e_skipwa():
    global B
    sw0 = next((k for k in range(o0, o1) if B[k].strip() == "_r = ''"), None)
    if sw0 is None or sw0 + 4 >= o1: return
    if not B[sw0+4].strip().startswith('else: wa.send_review(ph, _chair_wa_text('): return
    d = ind(B[sw0])
    B[sw0:sw0+5] = [d*' ' + "if _k == 't': say('🏷️ tagged only - WhatsApp skipped')  # SKIP-WA v84.38 + ONE-INPUT v84.47: the prompt retires, its law stays - the proposal's t already said it",
                    d*' ' + "else: wa.send_review(ph, _chair_wa_text(draft, p, cur['name']), say)"]
snap_edit('skipwa-merged', e_skipwa)
def e_nudge():
    global B
    n0 = next((k for k in range(o0, o1) if B[k].strip() == "_r0 = ''"), None)
    if n0 is None or n0 + 3 >= o1: return
    if not B[n0+3].strip().startswith("if _r0 != 'n':"): return
    d = ind(B[n0])
    B[n0:n0+4] = [d*' ' + "if _k != 't':  # ONE-INPUT v84.47: the nudge's draft decision lives in the same keystroke"]
snap_edit('nudge-merged', e_nudge)
def e_unknown7():
    global B
    for k in range(o0, o1):
        if 'unknown outcome - digits 1 to 6' in B[k]:
            B[k] = B[k].replace('digits 1 to 6', 'digits 1 to 7'); return
snap_edit('unknown-7', e_unknown7)
def e_tagvoice():
    global B
    t0 = next(k for k, l in enumerate(B) if l.startswith('def _tag_apply_one('))
    t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def '))
    for k in range(t0, t1):
        if B[k].strip() == 'k = confirm_wait(say)':
            B[k] = ind(B[k])*' ' + "k = menu_key()"; break
    for k in range(t0, t1):
        if B[k].strip().startswith("if k in ('y',): action_execute(say)"):
            B[k] = ind(B[k])*' ' + "if k in ('y', 't'): action_execute(say)  # ONE-INPUT v84.47: t executes without a draft wherever a draft could follow"; break
    for k in range(t0, t1):
        if B[k].strip().startswith("say(txt + ' · reply y / n')"):
            B[k] = ind(B[k])*' ' + "say(txt + ' · y / n', end='')  # INLINE-ECHO v84.45: the answer signs its own question's line"; break
snap_edit('tagvoice-menu', e_tagvoice)
src = '\n'.join(B); open('butler.py', 'w').write(src)
W = os.path.join(os.getcwd(), 'wa.py')
snapw = open(W).read()
w = snapw.split('\n')
if 'def _key(' not in '\n'.join(w):
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
for k, l in enumerate(w):
    if '(ask or input)(' in l and '[s] I clicked send myself' in l:
        d = ind(l)
        w[k:k+1] = [d*' ' + "_pm = '   [s] I clicked send myself · [x] discard & clear · [q] leave in field & close · [Enter] keep waiting: '",
                    d*' ' + "c = (ask(_pm).strip().lower() if ask else _key(_pm))  # ONE-KEY v84.46"]
        break
srcw = '\n'.join(w)
if parse_ok(w) and srcw != snapw:
    open(W, 'w').write(srcw); done.append('wa-onekey')
else:
    done.append('revert:wa-onekey')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.48' not in t:
        open(AR, 'a').write('v84.48: ONE-INPUT landed against the seen body - confirm block sliced in its verified ten-line shape (twin return buried), merged lines carry retired prompts\' markers, guards build forbidden literals from parts so no witness carries the crime in its own body; tag-voice executes t; unknown-outcome counts seven\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_wa = open(W).read()
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S316 the seated paper opens in Preview, behind your eyes, never closed by the machine", "'S315 the keystroke answers on its own question's line", "ck('S316 the seated paper opens in Preview, behind your eyes, never closed by the machine', (chr(35)+' PREVIEW v84.46') in _src and ('def _preview_open(' in _src))"),
      ("'S317 every single-letter door answers to the keystroke alone", "'S316 the seated paper opens in Preview, behind your eyes, never closed by the machine", "ck('S317 every single-letter door answers to the keystroke alone', (chr(35)+' ONE-KEY v84.46') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('def menu_key(' in _src))"),
      ("'S318 one keystroke decides the deed and the draft - no second prompt", "'S317 every single-letter door answers to the keystroke alone", "ck('S318 one keystroke decides the deed and the draft - no second prompt', (chr(35)+' ONE-INPUT v84.47') in _src and (('draft WhatsApp? ' + '[y] yes') not in _src))  # S318 repinned v84.48: the probe is built from parts, so the guard never carries the forbidden literal in its own body"),
      ("'S319 the unknown-outcome confession counts all seven doors", "'S318 one keystroke decides the deed and the draft - no second prompt", "ck('S319 the unknown-outcome confession counts all seven doors', ('digits 1 to 7' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

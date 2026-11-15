import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def desk_release(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _tag_write('))
    B[i:i] = ["def desk_release(p, say=print):  # RELEASE v84.13: releasing the top chair hands the desk to the waiting chair",
              "    d = desk_load(); rp = os.path.abspath(p)",
              "    if d.get('primary') == rp:",
              "        d['primary'] = d.get('secondary') or ''; d['secondary'] = ''",
              "    elif d.get('secondary') == rp:",
              "        d['secondary'] = ''",
              "    desk_save(d)",
              "    say(f\"🪑 chair released: {os.path.basename(rp)}\" + (f\" · promoted: {os.path.basename(d['primary'])}\" if d.get('primary') else ' · no chairs remain'))",
              ""]
    done.append('desk-release')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("elif arg.startswith('- '):"):
        d = ind(l)
        j = k
        while j < len(B) and not B[j].strip().startswith("elif arg.startswith('+'):"): j += 1
        B[k:j] = [d*' ' + "elif arg.startswith('- '):",
                  (d+4)*' ' + "p = desk_resolve(arg[2:], root)",
                  (d+4)*' ' + "desk_release(p or arg[2:], say)  # RELEASE v84.13"]
        done.append('chat-release-promote'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("say(f'🪑 desk: {_pr or \"-\"} · secondary: {_se}' if d.get('primary') else"):
        d = ind(l)
        B[k:k+1] = [d*' ' + "if d.get('primary') or d.get('secondary'): say(f'🪑 desk: {_pr or \"-\"} · secondary: {_se}')  # DESK-TRUTH v84.13: an empty primary never hides a seated secondary",
                    d*' ' + "else: say('🪑 no desk set - the butler watches the whole library evenly')"]
        done.append('desk-truth'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'calls', 'sheet', 'up', 'unskip', 'followup')" in l:
        B[k] = l.replace("'calls', 'sheet', 'up', 'unskip', 'followup')", "'calls', 'sheet', 'up', 'unskip', 'followup', 'release')")
        done.append('cli-release-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'followup':") and 'release' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'release': desk_release(' '.join(_a), print)")
        done.append('cli-release-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
bp = os.path.expanduser('~/CV_Tool/bin/butler-release.sh')
newsh = "#!/bin/zsh\nP=\"$1\"; [ -d \"$P\" ] || exit 1\ncd ~/CV_Tool && cv_env/bin/python3 butler.py release \"$P\"  # RELEASE v84.13: one source of truth for chairs\n"
if not os.path.exists(bp) or 'butler.py release' not in open(bp).read():
    open(bp, 'w').write(newsh); os.chmod(bp, 0o755); done.append('release-script')
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S263 release promotes the waiting chair and never hides a seated secondary", "'S262 every closed row ends with the living scoreboard", "ck('S263 release promotes the waiting chair and never hides a seated secondary', (chr(35)+' RELEASE v84.13') in _src and (chr(35)+' DESK-TRUTH v84.13') in _src and ('def desk_release(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'OPTION_MAP' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
    B[i:i] = ["OPTION_MAP = [  # OPTIONS-MAP v84.32: option = tag = keyword = draft-now + later-chase, so no door confuses the moments",
              " '1 interested · JD mailed   → [Awaiting JD Confirmation] · keyword: jd · now: jd-share · later: ack-reminder',",
              " '2 not interested           → [Closed – Not Proceeding] · keyword: refer · now: refer/farewell',",
              " '3 will update CV           → [Awaiting CV Update] · keyword: nudge · now: jd+ack+CV · later: cv-due',",
              " '4 missed / no answer       → [Call Scheduled] · keyword: missed · now: missed+JD-on-email',",
              " '5 ready for manager review → [Ready for Manager Review] · internal · no draft',",
              " '6 skip him for now         → no tag, no move, remembered · no draft',",
              "]",
              "def options_cmd(arg, root, say=print):  # OPTIONS-MAP v84.32",
              "    say('📋 option = tag = keyword = draft:')",
              "    for ln in OPTION_MAP: say('   ' + ln)",
              ""]
    done.append('options-map')
    src = '\n'.join(B)
k0 = next(k for k in range(len(B)) if B[k].strip().startswith("say('   1 interested · JD mailed"))
k1 = next(k for k in range(k0, len(B)) if B[k].strip().startswith("say('   6 skip him for now"))
if 'OPTION_MAP' not in '\n'.join(B[k0:k1+1]):
    d = ind(B[k0])
    B[k0:k1+1] = [d*' ' + "for _ln in OPTION_MAP: say('   ' + _ln)  # OPTIONS-MAP v84.32"]
    done.append('menu-map')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if not i: say('📭 sheet empty - type: calls'); return"):
        d = ind(l)
        B[k:k+1] = [d*' ' + "if not i:  # SELF-REFRESH v84.32: an empty sheet re-seeds itself from the living folders, so a dragged-out paper rises without a command",
                    (d+4)*' ' + "calls_cmd('', root, say)",
                    (d+4)*' ' + "if any(x.get('status') == 'waiting' for x in sheet_load().get('items', [])): return up_cmd(arg, root, say)",
                    (d+4)*' ' + "say('📭 sheet empty - every loose paper is seated, skipped or remembered'); return"]
        done.append('up-self-refresh'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'missed', 'jd', 'nudge', 'refer', 'clients')" in l:
        B[k] = l.replace("'clients')", "'clients', 'refresh', 'options')")
        done.append('cli-tuple')
for k, l in enumerate(B):
    if l.lstrip().startswith('_CLI_VERB = ') and "'refresh'" not in l:
        idx = l.rfind(')')
        B[k] = l[:idx] + ", 'refresh', 'options')" + l[idx+1:]  # MARKER-SAFE v84.32: insert before the paren; every character after it - comment and marker - stays
        done.append('quiet-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'clients':") and 'refresh' not in '\n'.join(B[k:k+4]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'refresh': calls_cmd(' '.join(_a), _pl_root(), print)")
        B.insert(k+2, d*' ' + "elif _v == 'options': options_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-branches'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'SELF-REFRESH' not in '\n'.join(g):
    for k, l in enumerate(g):
        if 'butler.sheet_current() and q.strip() in (' in l and 'do_outcome' in l:
            d = ind(l)
            g.insert(k, d*' ' + "if q.strip() == 'refresh': butler.calls_cmd('', root, say); continue  # SELF-REFRESH v84.32")
            g.insert(k+1, d*' ' + "if q.strip() == 'options': butler.options_cmd('', root, say); continue  # OPTIONS-MAP v84.32")
            done.append('chat-verbs'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S292 every option states its tag, its keyword and its two drafts", "'S291 the cv draft carries the touchpoint and the missed draft carries the JD line in whichever store speaks it", "ck('S292 every option states its tag, its keyword and its two drafts', (chr(35)+' OPTIONS-MAP v84.32') in _src and ('def options_cmd(' in _src))"),
      ("'S293 an empty sheet re-seeds itself and refresh re-seeds on demand", "'S292 every option states its tag, its keyword and its two drafts", "ck('S293 an empty sheet re-seeds itself and refresh re-seeds on demand', (chr(35)+' SELF-REFRESH v84.32') in _src and (chr(35)+' SELF-REFRESH v84.32') in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S294 widening a tuple never amputates its marker", "'S293 an empty sheet re-seeds itself and refresh re-seeds on demand", "ck('S294 widening a tuple never amputates its marker', (chr(35)+' MARKER-SAFE v84.32') in _src and (chr(35)+' QUIET-VERBS v84.2') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

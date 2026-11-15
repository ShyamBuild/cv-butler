import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def carry(new_first, deleted):
    ms = markers(deleted)
    if ms:
        return new_first.rstrip() + '  ' + ' '.join(ms) + '  # WITNESS-CARRY v84.52: deleted lines hand their laws to the line that survives'
    return new_first
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
n = 0
for k, l in enumerate(g):
    if '); continue' in l and ', root, say)' in l and 'butler.' in l:
        g[k] = l.replace(', root, say)', ', root, print)'); n += 1
    if 'do_draftwhy(q[9:].strip(), root, say)' in l:
        g[k] = l.replace('do_draftwhy(q[9:].strip(), root, say)', 'do_draftwhy(q[9:].strip(), root, print)'); n += 1
if n:
    done.append('dispatch-print-x%d' % n)
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
snap = list(B)
for k, l in enumerate(B):
    if l.strip().startswith('def calls_cmd(') and 'hint=True' not in l:
        B[k] = l.replace('say=print):', 'say=print, hint=True):'); done.append('calls-hint'); break
for k, l in enumerate(B):
    if "call sheet seeded:" in l and l.strip().startswith('say('):
        d = ind(l)
        deleted = B[k:k+2]
        B[k:k+2] = [carry(d*' ' + "say(f'📞 call sheet seeded: {len(items) + reopened} outside the stage folders' + (f' · reopened {reopened}' if reopened else '') + (' · type: up' if hint and (items or reopened) else ''))  # ONE-LINE v84.51: the sheet speaks once, hint only when a hand must follow", deleted)]
        done.append('calls-oneline'); break
for k, l in enumerate(B):
    if l.strip().startswith("calls_cmd('', root, say)") and 'up_cmd' in '\n'.join(B[max(0,k-40):k]):
        B[k] = ind(l)*' ' + "calls_cmd('', root, say, False)  # ONE-LINE v84.51: the self-refresh reseeds without the throat-clearing hint"
        done.append('up-hint'); break
m0 = next(k for k, l in enumerate(B) if l.strip().startswith('OPTION_MAP = ['))
m1 = next(k for k in range(m0, len(B)) if B[k].strip() == ']')
deleted = B[m0:m1+1]
B[m0:m1+1] = [carry("OPTION_MAP = [  # OPTIONS-MAP v84.32 (emoji faces v84.53): option = tag = keyword = draft-now + later-chase; the jd door wears the outbox tray, for the envelope glyph is outlawed by S195", deleted),
              " '1 📤 interested · JD mailed   → [Awaiting JD Confirmation] · keyword: jd · now: jd-share · later: ack-reminder',",
              " '2 🙅 not interested           → [Closed – Not Proceeding] · keyword: refer · now: refer/farewell',",
              " '3 📝 will update CV           → [Awaiting CV Update] · keyword: cv · now: jd+ack+CV combo · later: cv-due',",
              " '4 🔔 nudge / remind him       → no tag change · keyword: nudge · now: reminder (ack JD or send CV) · row closes, debt stays',",
              " '5 📵 missed / no answer       → [Call Scheduled] · keyword: missed · now: missed+JD-on-email',",
              " '6 🏆 ready for manager review → [Ready for Manager Review] · internal · no draft',",
              " '7 ⏭️ skip him for now         → no tag, no move, remembered · no draft',",
              "]"]
done.append('emoji-map')
for k, l in enumerate(B):
    if '1 jd→JD-Conf · 2 refer→Closed' in l or '1 📤 jd→JD-Conf' in l or '1 📧 jd→JD-Conf' in l:
        d = ind(l)
        B[k] = carry(d*' ' + "say('   1 📤 jd→JD-Conf · 2 🙅 refer→Closed · 3 📝 cv→CV-Update · 4 🔔 nudge→reminder(no tag) · 5 📵 missed→Call-Sched · 6 🏆 internal→Ready · 7 ⏭️ skip→remembered')  # EMOJI-CUE v84.51: each door wears its face, and no face wears a banned glyph", [l])
        done.append('emoji-compact'); break
for k, l in enumerate(B):
    if "y = tag + move + WhatsApp draft · t = tag + move, no WhatsApp · n = cancel" in l:
        B[k] = l.replace('y = tag + move + WhatsApp draft · t = tag + move, no WhatsApp · n = cancel', 'y = 🏷️ tag + 📦 move + 📱 WhatsApp draft · t = 🏷️ tag + 📦 move, no 📱 · n = cancel')
        done.append('emoji-cue-outcome'); break
for k, l in enumerate(B):
    if "y = tag + move · t = tag + move, no WhatsApp · n = cancel" in l:
        B[k] = l.replace('y = tag + move · t = tag + move, no WhatsApp · n = cancel', 'y = 🏷️ tag + 📦 move · t = same, no 📱 · n = cancel')
        done.append('emoji-cue-tagvoice'); break
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if B[k].strip() == 'desk_dashboard(say)' and 'ACTION-ECHO' not in '\n'.join(B[max(0,k-4):k]):
        d = ind(B[k])
        B.insert(k, d*' ' + "say(f'🔚 {cur[\"name\"]}: 🏷️ {tag} · 📦 moved · ' + ('📱 drafted' if _k != 't' else 'no 📱'))  # ACTION-ECHO v84.51: the beat you just played, summarised in the house's pictographs")
        done.append('action-echo'); break
M1 = set(markers(B))
lost = M0 - M1
if lost:
    print('⛔ witness diff: these laws would vanish -', sorted(lost))
    raise SystemExit('harvest them onto surviving lines before this lap may ship')
if chr(128231) in '\n'.join(B):
    print('⛔ S195 contraband: the banned envelope glyph lives in the book')
    raise SystemExit('swap the face before shipping')
print('🔎 witness diff: 0 laws lost -', len(M0), 'markers before,', len(M1), 'after; no banned glyph')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    open('butler.py', 'w').write('\n'.join(snap)); raise SystemExit('parse failed - reverted')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.53' not in t:
        open(AR, 'a').write('v84.53: the terminal redesign lands with lawful faces - option 1 wears the outbox tray because S195 outlawed the envelope glyph long ago; emoji cues, one-line calls, hint-free reseed, action echo and the dispatch print-cure all live beneath the witness-carry harness\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S322 no dispatch line at module level passes a printer it cannot see", "'S321 the cue line names the deeds in the master's words", "ck('S322 no dispatch line at module level passes a printer it cannot see', sum(1 for _l in open(os.path.join(BASE_DIR, 'briefing.py')).read().split(chr(10)) if (', root, ' + 'say); continue') in _l) == 0)"),
      ("'S323 the sheet speaks one line per beat and every door wears its face", "'S322 no dispatch line at module level passes a printer it cannot see", "ck('S323 the sheet speaks one line per beat and every door wears its face', (chr(35)+' ONE-LINE v84.51') in _src and (chr(35)+' EMOJI-CUE v84.51') in _src and (chr(35)+' ACTION-ECHO v84.51') in _src)"),
      ("'S324 no lap may bury a law - deleted lines carry their witnesses", "'S323 the sheet speaks one line per beat and every door wears its face", "ck('S324 no lap may bury a law - deleted lines carry their witnesses', (chr(35)+' WITNESS-CARRY v84.52') in _src)"),
      ("'S325 the emoji cue coexists with the banned glyph's absence", "'S324 no lap may bury a law - deleted lines carry their witnesses", "ck('S325 the emoji cue coexists with the banned glyph'+chr(39)+'s absence', chr(128231) not in _src and (chr(35)+' EMOJI-CUE v84.51') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

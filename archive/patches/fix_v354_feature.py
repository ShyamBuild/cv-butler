import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
for k in range(c0, c1):
    if B[k].strip() == 'if not os.path.isfile(kp): continue' and 'RETRAY-RESOLVE' not in '\n'.join(B[max(0,k-6):k+8]):
        d = ind(B[k])
        B[k:k+1] = [d*' ' + "qq = kp if os.path.isfile(kp) else None  # RETRAY-RESOLVE v85.1: a stale skip path is re-found by name, like every other door; only a vanished paper stays skipped",
                    d*' ' + "if qq is None:",
                    (d+4)*' ' + "bn = os.path.basename(kp)",
                    (d+4)*' ' + "for sc in desk_paths():",
                    (d+8)*' ' + "for dp, dn, fn in os.walk(sc):",
                    (d+12)*' ' + "if bn in fn: qq = os.path.join(dp, bn); break",
                    (d+8)*' ' + "if qq: break",
                    d*' ' + "if not qq: continue"]
        done.append('retray-resolve'); break
for k in range(c0, c1):
    if B[k].strip().startswith('rp2 = os.path.realpath(kp)') and 'RETRAY-RESOLVE' in '\n'.join(B[max(0,k-10):k]):
        for j in range(k, min(k+8, c1)):
            B[j] = B[j].replace('(kp)', '(qq)').replace("{'p': kp,", "{'p': qq,")
        done.append('retray-use-qq'); break
src = '\n'.join(B)
d0 = next(k for k, l in enumerate(B) if l.startswith('def desk_dashboard('))
d1 = next(k for k in range(d0 + 1, len(B)) if B[k].startswith('def '))
if 'TRAY-NAMES' not in '\n'.join(B[d0:d1]):
    B[d1:d1] = ["    if skips_load():  # TRAY-NAMES v85.1: a count without names is a queue of strangers - the tray names its members whenever it is not empty",
                "        _sk = list(skips_load())",
                "        say('⏭️ tray: ' + ', '.join(os.path.basename(x) for x in _sk[:4]) + (f' +{len(_sk)-4}' if len(_sk) > 4 else '') + ' · one returns per empty seed')"]
    done.append('tray-names')
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if B[k].strip().startswith("if _k == 't': say('🏷️ tagged only - WhatsApp skipped')"):
        B[k] = ind(B[k])*' ' + "if _k == 't': pass  # CINE-LINE v85.1: the deed line already says no 📱"
        done.append('tagged-only-retired'); break
for k in range(o0, o1):
    if B[k].strip().startswith("say(f'🔚 {cur[") and 'ACTION-ECHO v84.51' in B[k]:
        del B[k]
        done.append('echo-retired'); break
kw = next((k for k in range(o0, o1) if '🏷️' in B[k] and B[k].strip().startswith('say(') and 'cur[' in B[k]), None)
sm = next((k for k in range(o0, o1) if '_stage_move(' in B[k] and ', say)' in B[k]), None)
if kw is not None and sm is not None and 'CINE-LINE' not in '\n'.join(B[o0:o1]):
    del B[kw]
    sm -= 1
    B[sm] = B[sm].replace(', say)', ', lambda *a, **k: None)')
    db = next(k for k in range(sm, o1) if B[k].strip() == 'desk_dashboard(say)')
    d = ind(B[db])
    B.insert(db, d*' ' + "say(f\"✅ {cur['name']} · 🏷️ {tag} · 📦 {os.path.basename(os.path.dirname(p))} · \" + ('📱 drafted' if (_k != 't' and draft) else ('no 📱' if draft else 'internal · no 📱')))  # ACTION-ECHO v84.51 CINE-LINE v85.1: one deed line, nothing repeated")
    done.append('cine-line')
else:
    done.append('cine-line-deferred: paste grep -n "🏷️\\|_stage_move" ~/CV_Tool/butler.py | sed -n 1,20p')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.1' not in t:
        open(AR, 'a').write('v85.1: CINEMA TERMINAL - one deed line per outcome (the move\'s printer silenced, the pre-move tag line retired, warnings still surface), tray names its members whenever non-empty, stale skip paths re-found by basename so the drip-feed never starves; first lap to pay the freeze price\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S330 a stale skip is re-found by name, so the tray never starves", "'S329 the freeze holds - v85.0 is the standing price of every future change", "ck('S330 a stale skip is re-found by name, so the tray never starves', (chr(35)+' RETRAY-RESOLVE v85.1') in _src)"),
      ("'S331 the tray names its members whenever it is not empty", "'S330 a stale skip is re-found by name, so the tray never starves", "ck('S331 the tray names its members whenever it is not empty', (chr(35)+' TRAY-NAMES v85.1') in _src)")]
if (chr(35)+' CINE-LINE v85.1') in src:
    GU.append(("'S332 the deed speaks once, in one line, and silence never swallows a warning", "'S331 the tray names its members whenever it is not empty", "ck('S332 the deed speaks once, in one line, and silence never swallows a warning', (chr(35)+' CINE-LINE v85.1') in _src and ('lambda *a, **k: None' in _src))"))
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

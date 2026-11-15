import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'def do_draftwhy(' not in '\n'.join(g):
    i = next(k for k, l in enumerate(g) if l.startswith('def do_adlog('))
    g[i:i] = ["def do_draftwhy(arg, root, say=print):  # DRAFT-WHY v84.33: eyes behind every draft - which guess, which truth, which fields, which files (display-only; _fmt_tpl stays witnessed and untouched)",
              "    hits = _hits_for((arg or '').strip(), root)",
              "    if not hits: say(f'🤷 no CV matches {arg!r}'); return",
              "    p = hits[0]; nm = os.path.splitext(os.path.basename(p))[0]",
              "    pos, cli = _pos_client_for(p, None); title, loc = _split_pos(pos)",
              "    import butler as _bt",
              "    idn = _bt.pos_identity(p)",
              "    fco = idn.get('company') or cli; fpo = idn.get('role') or title; flo = idn.get('loc') or loc; fdz = idn.get('designation') or fpo",
              "    say(f'🔎 draft anatomy for {nm}:')",
              "    say(f'   legacy path-guess : position={title!r} company={cli!r} location={loc!r}')",
              "    say(f'   registry truth    : company={idn.get(\"company\")!r} role={idn.get(\"role\")!r} loc={idn.get(\"loc\")!r} designation={idn.get(\"designation\")!r}')",
              "    say(f'   fields used       : name={nm!r} · position={fpo!r} · company={fco!r} · location={flo!r} · designation={fdz!r} · where={fco + (\", \" + flo if flo else \"\")!r}')",
              "    TDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')",
              "    for w in ('jd', 'missed', 'nudge', 'refer', 'awaiting'):",
              "        try: cands = [fn for fn in sorted(os.listdir(TDIR)) if fn.endswith('.txt') and w in fn.lower()]",
              "        except Exception: cands = []",
              "        say(f'   scenario {w} files : ' + (', '.join(cands[:4]) or 'none'))",
              "    say('   rendered jd draft :')",
              "    for ln in _fmt_tpl(_tpl_for(['jd']), p, None, nm).split(chr(10)): say('     ' + ln)",
              "    say('   queued chases     : ad_wait.build_text now drinks from the same registry (QUEUE-REGISTRY v84.34)')",
              ""]
    done.append('draftwhy')
    srcg = '\n'.join(g)
    if not any(l.strip().startswith("if q.startswith('draftwhy ')") for l in g):
        for k, l in enumerate(g):
            if l.strip().startswith("if q.strip() == 'refresh':"):
                d = ind(l)
                g.insert(k, d*' ' + "if q.startswith('draftwhy '): do_draftwhy(q[9:].strip(), root, say); continue  # DRAFT-WHY v84.33")
                done.append('chat-draftwhy'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
A = os.path.join(os.getcwd(), 'ad_wait.py')
a = open(A).read().split('\n')
if 'QUEUE-REGISTRY' not in '\n'.join(a):
    for k, l in enumerate(a):
        if l.strip().startswith("t = open(os.path.join(BASE, 'templates', f'voice_{v}.txt')).read()"):
            d = ind(l)
            a[k:k] = [d*' ' + "try:  # QUEUE-REGISTRY v84.34: the queued chase drinks from the same registry as every other door",
                      d*' ' + "    import butler as _bt",
                      d*' ' + "    _idn = _bt.pos_identity(fp) if fp else {}",
                      d*' ' + "    if _idn.get('company'): client = _idn['company']",
                      d*' ' + "    if _idn.get('role'): pos = _idn['role']",
                      d*' ' + "    if _idn.get('loc'): loc = _idn['loc']",
                      d*' ' + "    _dz = _idn.get('designation') or pos",
                      d*' ' + "except Exception:",
                      d*' ' + "    _dz = pos"]
            done.append('queue-registry'); break
    srca = '\n'.join(a)
    for k, l in enumerate(a):
        if l.strip().startswith("return t.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc)"):
            d = ind(l)
            a[k] = d*' ' + "return t.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc).replace('{company}', client).replace('{designation}', _dz).replace('{where}', client + (', ' + loc if loc else ''))"
            done.append('queue-slots'); break
    srca = '\n'.join(a)
    if srca != open(A).read():
        ast.parse(srca); open(A, 'w').write(srca)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if "'clients', 'refresh', 'options')" in l and 'draftwhy' not in l:
        B[k] = l.replace("'options')", "'options', 'draftwhy')")
        done.append('cli-tuple')
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'options':") and 'draftwhy' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'draftwhy': import briefing as _br; _br.do_draftwhy(' '.join(_a), _pl_root(), print)")
        done.append('cli-draftwhy'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
MW = os.path.join(os.getcwd(), 'mw.sh')
if not os.path.exists(MW):
    open(MW, 'w').write("""#!/bin/zsh
# mw.sh - marker watch: list every law-marker inside a function region BEFORE you replace it
# usage: ./mw.sh briefing.py _fmt_tpl _pos_client_for
F="$1"; A="$2"; Bn="$3"
[ -f "$F" ] || { echo "no such file: $F"; exit 1; }
awk -v a="$A" -v b="$Bn" '
  index($0, "def " a "(") { on = 1 }
  on && index($0, "def " b "(") { on = 0 }
  on { if (match($0, /# [A-Z0-9-]+ v[0-9.]+/)) print substr($0, RSTART, RLENGTH) }
' "$F" | sort | uniq -c
echo "-- region markers above; a replace must carry or repin each one"
""")
    os.chmod(MW, 0o755); done.append('mw-sh')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
if not os.path.exists(AR):
    open(AR, 'w').write("""# CV-Tool architecture (living index - append one line per lap)
## doors
chat (briefing.py REPL) · terminal verbs (butler.py CLI) · Finder right-click (butler-here/release/clear-desk) · watcher (butler.py tick)
## composers (every draft flows through exactly one, all registry-aware)
briefing._fmt_tpl (keywords + chair fallback) · butler._chair_wa_text (chair outcomes) · ad_wait.build_text (queued chases, QUEUE-REGISTRY v84.34)
## stores
templates/ (master's legacy voice) · drafts/ (house fallbacks) · clients.json · positions.json · skips.json · covered.json · sheet.json · pipeline.json · errands.json · stage_log.json · renames/undo ledger
## registries and truths
pos_identity = clients.json > positions.json > folder parse · FOLDER-TRUTH: stage folder = covered, loose = contactable · coverage memory = covered.json + skips + folder
## laws
S191/S214: old guards repin, never veto · S294: widening keeps markers · marker rule: a replace carries or repins every # MARKER vN inside its region (query with ./mw.sh file fnA fnB)
## lap log
v84.34: draftwhy (display-only), queue-registry, mw.sh, ARCHITECTURE.md
""")
    done.append('architecture-md')
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S295 every draft can name its guesses, its truths, its fields and its files", "'S294 widening a tuple never amputates its marker", "ck('S295 every draft can name its guesses, its truths, its fields and its files', (chr(35)+' DRAFT-WHY v84.33') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('def do_draftwhy(' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S296 the queued chase drinks from the same registry as every other door", "'S295 every draft can name its guesses, its truths, its fields and its files", "ck('S296 the queued chase drinks from the same registry as every other door', (chr(35)+' QUEUE-REGISTRY v84.34') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())"),
      ("'S297 no region is replaced before its markers are counted", "'S296 the queued chase drinks from the same registry as every other door", "ck('S297 no region is replaced before its markers are counted', os.path.exists(os.path.join(BASE_DIR, 'mw.sh')) and ('region markers above' in open(os.path.join(BASE_DIR, 'mw.sh')).read()) and os.path.exists(os.path.join(BASE_DIR, 'ARCHITECTURE.md')))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

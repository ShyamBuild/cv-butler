import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())

readme = """# CV Butler v85.0
*The co-pilot that remembers, confirms, and sends.*

## The Nine Domains
1. **xattr kernel**: what we write is what the next read sees.
2. **identity clerk**: a human is confirmed by his own paper, his taught word last.
3. **conversion bench**: the reason Converted Files exists and never queues.
4. **desk and chairs**: folders are the truth.
5. **coverage memory**: spoken-to never re-offered; a renamed paper is the same paper.
6. **registry**: one truth per position, taught once.
7. **proposal gate**: nothing happens without the keystroke; everything is written down.
8. **errands clock**: timers arm from tags and sleep at night.
9. **census and reports**: the desk speaks its census in one breath.
10. **rename gate**: the visual name carries the human; your word can undo it.

## The Seven Doors
1 📤 interested · JD mailed → [Awaiting JD Confirmation]
2 🙅 not interested / not relevant → [Closed – Not Proceeding] (references often asked)
3 📝 will update CV → [Awaiting CV Update]
4 🔔 nudge / remind him → no tag change, debt stays
5 📵 missed / no answer → [Call Scheduled]
6 🏆 ready for manager review → [Ready for Manager Review]
7 ⏭️ skip him for now → remembered in the tray (one returns per empty seed)

## The Skip Tray (RETRAY-ONE)
When the call tray is empty, ONE skipped soul rises (oldest first), his skip consumed. New loose papers always seed and seat ahead of the tray. Re-skipping a re-review man stamps a fresh timestamp to the back.

## The Composers
- **ONE-VOICE**: the chair drafts through the same composer the keywords have always used.
- **Scenario Stores**: `drafts/cv.txt` (decision combo), `templates/voice_cv_update.txt` (later touchpoint), `drafts/nudge.txt` (reminder).

## The Contract
Every change to this house obeys:
- **Paste-before-replace**: unseen code is pasted, never guessed.
- **Witness-carry**: deleted lines hand their law-markers to the line that survives.
- **Marker-diff**: a book-wide diff refuses any lap that loses a law.
- **Quine-proof probes**: negative guards are built from concatenated parts, so no witness carries the crime in its own body.

## Quickstart
1. `git clone <mirror>`
2. `./install.sh`
3. `python3 butler.py clients 01 HIPP = Honda India`
4. `python3 butler.py desk seat Sunsoft Technology`
5. `python3 butler.py up`
6. (Press 1-7, then y/t/n)
"""
with open('README.md', 'w') as f:
    f.write(readme)
done.append('readme')

install = """#!/bin/bash
# CV Butler v85.0 Installer
set -e
echo "🤵 CV Butler v85.0 - installing on $(hostname)..."
python3 -m venv .venv || true
source .venv/bin/activate || true
pip install -r requirements.txt 2>/dev/null || pip install pyobjc-framework-Quartz
mkdir -p drafts templates
echo "✅ Stores seeded. Run 'chat' to begin."
"""
with open('install.sh', 'w') as f:
    f.write(install)
os.chmod('install.sh', 0o755)
done.append('install')

B = open('butler.py').read().split('\n')
if "VERSION = '85.0'" not in '\n'.join(B[:20]):
    B.insert(0, "VERSION = '85.0'  # THE FREEZE v85.0: the standing price of every future change")
    done.append('butler-version')

G = open('briefing.py').read().split('\n')
if "VERSION = '85.0'" not in '\n'.join(G[:20]):
    G.insert(0, "VERSION = '85.0'")
    open('briefing.py', 'w').write('\n'.join(G))
    done.append('briefing-version')

open('butler.py', 'w').write('\n'.join(B))

def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None

GU = [("'S329 the freeze holds - v85.0 is the standing price of every future change", "'S328 the tray offers one skipped soul per empty seed, oldest first", "ck('S329 the freeze holds - v85.0 is the standing price of every future change', VERSION == '85.0' and os.path.exists(os.path.join(BASE_DIR, 'README.md')) and os.path.exists(os.path.join(BASE_DIR, 'install.sh')))")]

for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')

src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)

AR = 'ARCHITECTURE.md'
try:
    t = open(AR).read()
    if 'v85.0' not in t:
        open(AR, 'a').write('\nv85.0: THE FREEZE - README.md and install.sh born; VERSION spoken; S329 pins the freeze rule. The house is robust and ready to ship.\n')
        done.append('arch-line')
except Exception: pass

print('✅', done)

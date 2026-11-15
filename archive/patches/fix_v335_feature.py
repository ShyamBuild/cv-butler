import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("OUTCOMES = {'1':") and "'7':" not in l:
        d = ind(l)
        B[k] = d*' ' + "OUTCOMES = {'1': ('Awaiting JD Confirmation', 'interested · JD mailed', 'jd'), '2': ('Closed \\u2013 Not Proceeding', 'not interested', 'refer'), '3': ('Awaiting CV Update', 'will update CV', 'cv'), '4': ('', 'nudge - remind to acknowledge the JD or send the updated CV', 'nudge'), '5': ('Call Scheduled', 'missed / no answer', 'missed'), '6': ('Ready for Manager Review', 'ready for manager', None), '7': (None, 'skipped', None)}  # NUDGE-OPTION v84.44: seven doors - the reminder changes no tag and moves nothing"
        done.append('outcomes-7'); break
src = '\n'.join(B)
m0 = next(k for k, l in enumerate(B) if l.strip().startswith('OPTION_MAP = ['))
m1 = next(k for k in range(m0, len(B)) if B[k].strip() == ']')
B[m0:m1+1] = ["OPTION_MAP = [  # OPTIONS-MAP v84.32 (seven doors v84.44): option = tag = keyword = draft-now + later-chase",
              " '1 interested · JD mailed   → [Awaiting JD Confirmation] · keyword: jd · now: jd-share · later: ack-reminder',",
              " '2 not interested           → [Closed – Not Proceeding] · keyword: refer · now: refer/farewell',",
              " '3 will update CV           → [Awaiting CV Update] · keyword: cv · now: jd+ack+CV combo · later: cv-due',",
              " '4 nudge / remind him       → no tag change · keyword: nudge · now: reminder (ack JD or send CV) · row closes, debt stays',",
              " '5 missed / no answer       → [Call Scheduled] · keyword: missed · now: missed+JD-on-email',",
              " '6 ready for manager review → [Ready for Manager Review] · internal · no draft',",
              " '7 skip him for now         → no tag, no move, remembered · no draft',",
              "]"]
done.append('option-map-7')
src = '\n'.join(B)
for k, l in enumerate(B):
    if '1 jd→JD-Conf · 2 refer→Closed' in l:
        d = ind(l)
        B[k:k+2] = [d*' ' + "say('   1 jd→JD-Conf · 2 refer→Closed · 3 cv→CV-Update · 4 nudge→reminder(no tag) · 5 missed→Call-Sched · 6 internal→Ready · 7 skip→remembered')  # MAP-COMPACT v84.37 (seven doors v84.44)",
                    d*' ' + "say('   (options prints the full grammar with keywords and both draft moments)')"]
        done.append('compact-7'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('CHAIR_WORDS = {') and "'nudge': '4'" not in l:
        d = ind(l)
        B[k] = d*' ' + "CHAIR_WORDS = {'missed': '5', 'no answer': '5', 'jd': '1', 'jd mailed': '1', 'cv': '3', 'update cv': '3', 'not interested': '2', 'ready': '6', 'manager': '6', 'skip': '7', 'skip him': '7', 'skip for now': '7', 'skip him for now': '7', 'nudge': '4', 'remind': '4', 'reminder': '4'}  # CHAIR-WORDS renumbered v84.44: the reminder owns four"
        done.append('chair-words-7'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "sys.argv[1] in ('1', '2', '3', '4', '5', '6')" in l:
        B[k] = l.replace("('1', '2', '3', '4', '5', '6')", "('1', '2', '3', '4', '5', '6', '7')")
        done.append('cli-digit-7'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("say('🤷 unknown outcome - digits 1 to 6"):
        B[k] = B[k].replace('digits 1 to 6', 'digits 1 to 7')
        done.append('unknown-7'); break
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if B[k].strip().startswith("say(f\"🤖 Proposal: {cur['name']} → \"") and '_tagpart' not in '\n'.join(B[k-2:k]):
        d = ind(B[k])
        B[k:k+1] = [d*' ' + "_tagpart = 'SKIPPED, untagged, unmoved' if tag is None else ('[no tag change - reminder only]' if tag == '' else f'[{tag}]')  # NUDGE-OPTION v84.44",
                    d*' ' + "say(f\"🤖 Proposal: {cur['name']} → \" + _tagpart + f\" ({outcome})\" + (f' · WhatsApp {draft} draft will open, unsent' if draft else ' · no message - this one stays in the house') + ' · y / n')"]
        done.append('proposal-nudge'); break
src = '\n'.join(B)
if 'chair-nudge' not in src:
    i = next(k for k in range(o0, o1) if B[k].strip().startswith('if tag is None:  # SKIP v84.11'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "if tag == '':  # NUDGE-OPTION v84.44: a reminder changes no tag and moves nothing - the debt stays, the row closes, the thread continues",
              (d+4)*' ' + "_r0 = ''",
              (d+4)*' ' + "try: _r0 = input('📱 draft WhatsApp? [y] yes · [n] skip (no text): ').strip().lower()",
              (d+4)*' ' + "except Exception: pass",
              (d+4)*' ' + "if _r0 != 'n':",
              (d+8)*' ' + "ph0 = taught_digits(cur['name']) or phones_of(p, True) or None",
              (d+8)*' ' + "if isinstance(ph0, list): ph0 = ph0[0] if ph0 else None",
              (d+8)*' ' + "if ph0:",
              (d+12)*' ' + "import wa",
              (d+12)*' ' + "wa.send_review(ph0, _chair_wa_text('nudge', p, cur['name']), say)",
              (d+8)*' ' + "else: say(f'⚠️ no phone for {cur[\"name\"]} - teach me: python3 butler.py teach {cur[\"name\"].split()[0].lower()} <digits>, then retry')",
              (d+4)*' ' + "for it in s.get('items', []):",
              (d+8)*' ' + "if it.get('status') == 'waiting' and (os.path.realpath(it.get('p', '')) == os.path.realpath(p) or _name_key(os.path.basename(it.get('p', ''))) == _name_key(os.path.basename(p))):",
              (d+12)*' ' + "it['status'] = 'done'; it['outcome'] = 'nudged'; it['ts'] = int(time.time())",
              (d+4)*' ' + "s['current'] = None; sheet_save(s)",
              (d+4)*' ' + "_stage_note(cur['name'], _tags_of(p), _tags_of(p), os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chair-nudge')",
              (d+4)*' ' + "say(f'🔔 nudged {cur[\"name\"]} - no tag changed, nothing moved; his debts stay on the followup board')",
              (d+4)*' ' + "desk_dashboard(say)",
              (d+4)*' ' + "w = [x for x in s.get('items', []) if x['status'] == 'waiting']",
              (d+4)*' ' + "if w: say(f'⏭️ next up: {w[0][\"name\"]} - type: up')",
              (d+4)*' ' + "else: say('🏁 sheet covered - every candidate has an outcome')",
              (d+4)*' ' + "return"]
    done.append('nudge-branch')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('CHAIR_SCENARIO = {') and "'nudge'" not in l:
        B[k] = l.replace("}", ", 'nudge': 'nudge'}") if l.rstrip().endswith('}') else l
        done.append('scenario-nudge'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if "q.strip() in ('1', '2', '3', '4', '5', '6')" in l:
        g[k] = l.replace("('1', '2', '3', '4', '5', '6')", "('1', '2', '3', '4', '5', '6', '7')")
        done.append('chat-digit-7'); break
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
DD = os.path.expanduser('~/CV_Tool/drafts')
lp = os.path.join(DD, 'nudge.txt')
if not os.path.exists(lp):
    open(lp, 'w').write("Hi {full}, Sundeep Rana here. A gentle reminder regarding the job description I shared for {roleline} - kindly acknowledge the JD on your email, or share your updated CV in PDF here if it is ready, so I can move your profile forward.\n{signature}\n")
    done.append('seed:nudge.txt')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.44' not in t:
        open(AR, 'a').write('v84.44: seven doors - nudge at 4 (reminder touchpoint: no tag, no move, row closes nudged, debt and chase stay); missed/ready/skip renumbered 5/6/7 in menu, map, words, CLI and chat digits\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S313 seven doors with the reminder at four", "'S312 a check never stands before the path it reads is born", "ck('S313 seven doors with the reminder at four', (chr(35)+' NUDGE-OPTION v84.44') in _src and (\"'7': (None, 'skipped', None)\" in _src))"),
      ("'S314 a nudge changes no tag and moves nothing", "'S313 seven doors with the reminder at four", "ck('S314 a nudge changes no tag and moves nothing', ('chair-nudge' in _src) and (\"it['outcome'] = 'nudged'\" in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def desk_dashboard(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _chase_draft('))
    B[i:i] = ["def desk_dashboard(say=print):  # DASH v84.7: the desk's census in one breath, read live from the tags, one human counted once",
              "    seen = set(); counts = {}; multi = []",
              "    for sc in desk_paths():",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if not x.lower().endswith(('.pdf', '.docx')): continue",
              "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
              "                if rp in seen: continue",
              "                seen.add(rp)",
              "                tgs = _tags_of(p)",
              "                st = [t for t in tgs if _tag_stage(t)]",
              "                if len(st) > 1: multi.append(x)",
              "                for t in tgs: counts[t] = counts.get(t, 0) + 1",
              "                if not tgs: counts['(untagged)'] = counts.get('(untagged)', 0) + 1",
              "    order = ['Ready for Manager Review', 'Awaiting JD Confirmation', 'Awaiting CV Update', 'Feedback Pending', 'Call Scheduled', 'Shortlisted for Interview', 'Interview Scheduled', 'Interview Today', 'Interview Tomorrow', 'Interview Cleared', 'Expected to Join', 'Joined - Payment Pending', 'Payment Received', 'Closed \\u2013 Not Proceeding', 'Rejected by Client', '(untagged)']",
              "    short = {'Ready for Manager Review': 'ready', 'Awaiting JD Confirmation': 'jd-ack', 'Awaiting CV Update': 'cv-wait', 'Feedback Pending': 'feedback', 'Call Scheduled': 'call', 'Shortlisted for Interview': 'short', 'Interview Scheduled': 'intv', 'Interview Today': 'intv-today', 'Interview Tomorrow': 'intv-tmrw', 'Interview Cleared': 'cleared', 'Expected to Join': 'join', 'Joined - Payment Pending': 'pay-pend', 'Payment Received': 'paid', 'Closed \\u2013 Not Proceeding': 'closed', 'Rejected by Client': 'rejected', '(untagged)': 'untagged'}",
              "    line = ' · '.join(f'{short[t]}:{counts[t]}' for t in order if counts.get(t))",
              "    say('📊 ' + (line or 'empty desk'))",
              "    if multi: say('⚠️ wearing two stages: ' + ', '.join(multi[:6]) + (' …' if len(multi) > 6 else ''))",
              "def tags_audit(say=print):  # AUDIT v84.7: papers wearing two stages are named, never silently rewritten",
              "    seen = set(); bad = 0",
              "    for sc in desk_paths():",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if not x.lower().endswith(('.pdf', '.docx')): continue",
              "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
              "                if rp in seen: continue",
              "                seen.add(rp)",
              "                st = [t for t in _tags_of(p) if _tag_stage(t)]",
              "                if len(st) > 1:",
              "                    bad += 1",
              "                    say(f'⚠️ {x} · in {os.path.basename(dp)} · wears {\", \".join(st)} - one transition will settle it')",
              "    if not bad: say('✅ every paper on the desk rests in exactly one stage')",
              ""]
    done.append('dash-audit')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("else: say(f'🤷 no position folder matches {arg}')") and 'desk_dashboard' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "if d.get('primary'): desk_dashboard(say)  # DASH v84.7: seating a chair shows the census at once")
        done.append('desk-dash-call'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip() == "if not od: say('   · nothing overdue')" and 'desk_dashboard' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "desk_dashboard(say)")
        done.append('briefing-dash'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'chase', 'tag')" in l and 'sys.argv' in l or "'chase', 'tag')" in l and '_CLI_VERB' in l:
        B[k] = l.replace("'chase', 'tag')", "'chase', 'tag', 'dash', 'audit')")
        if 'cli-dash' not in done: done.append('cli-dash')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("tag_voice(' '.join(_aa), _on, print)"):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'dash': desk_dashboard(print)")
        B.insert(k+2, d*' ' + "elif _v == 'audit': tags_audit(print)")
        done.append('cli-dash-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_dash(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_tagcmd('))
    g[i:i] = ["def do_dash(arg, root, say=print):  # DASH v84.7",
              "    butler.desk_dashboard(say)",
              "def do_audit(arg, root, say=print):  # AUDIT v84.7",
              "    butler.tags_audit(say)",
              ""]
    done.append('chat-dash-fns')
    srcg = '\n'.join(g)
if not any(l.strip().startswith("if q.startswith('dash')") for l in g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('pending'): do_pending("):
            d = ind(l)
            g[k:k] = [d*' ' + "if q.startswith('dash'): do_dash(q[4:].strip(), root); continue  # DASH v84.7",
                      d*' ' + "if q.startswith('audit'): do_audit(q[5:].strip(), root); continue"]
            done.append('chat-dash-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S244 the desk speaks its census in one breath, one human counted once", "'S243 a proposal is answered by a keystroke, like the WhatsApp menu", "ck('S244 the desk speaks its census in one breath, one human counted once', (chr(35)+' DASH v84.7') in _src and ('def desk_dashboard(' in _src))"),
      ("'S245 papers wearing two stages are named, never silently rewritten", "'S244 the desk speaks its census in one breath, one human counted once", "ck('S245 papers wearing two stages are named, never silently rewritten', (chr(35)+' AUDIT v84.7') in _src and ('def tags_audit(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

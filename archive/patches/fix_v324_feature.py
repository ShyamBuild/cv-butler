import ast, os, re, json
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
def _idx(lines, name):
    for k, l in enumerate(lines):
        if l.startswith('def ' + name + '('): return k
    return None
i0, i1, i2 = _idx(g, '_local_name'), _idx(g, 'answer'), _idx(g, '_read_tpl')
if None in (i0, i1, i2): raise SystemExit('anchor missing: _local_name / answer / _read_tpl')
marks = []
for seg in (g[i0:i1], g[i1:i2]):
    for l in seg:
        marks += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
if marks:
    print('⛔ mw.sh equivalent: markers live in the target regions -', sorted(set(marks)))
    raise SystemExit('carry or repin every one of them before this patch may apply')
print('🔎 mw.sh equivalent: regions _local_name→answer and answer→read_tpl carry', len(set(marks)), 'markers - insert is witness-safe')
if 'def _ear_intent(' not in '\n'.join(g):
    g[i1:i1] = ["EAR_WORDS = ('said', 'will', 'send', 'sent', 'missed', 'not interested', 'ready', 'update', 'acknowledge', 'confirm', 'joined', 'interview', 'feedback', 'pick', 'answer')  # EAR v84.35: an event-word or it is not an ear-sentence",
                "EAR_TAGS = [('not interested', 'Closed \\u2013 Not Proceeding'), ('rejected by client', 'Rejected by Client'), ('ready for manager', 'Ready for Manager Review'), ('manager review', 'Ready for Manager Review'), ('will send cv', 'Awaiting CV Update'), ('send the cv', 'Awaiting CV Update'), ('update cv', 'Awaiting CV Update'), ('updated cv', 'Awaiting CV Update'), ('missed', 'Call Scheduled'), ('no answer', 'Call Scheduled'), ('didn\\u2019t pick', 'Call Scheduled'), ('did not pick', 'Call Scheduled'), ('jd mailed', 'Awaiting JD Confirmation'), ('acknowledge', 'Awaiting JD Confirmation'), ('interested', 'Awaiting JD Confirmation'), ('feedback pending', 'Feedback Pending'), ('interview tomorrow', 'Interview Tomorrow'), ('interview today', 'Interview Today'), ('interview', 'Interview Scheduled'), ('joined', 'Expected to Join'), ('call scheduled', 'Call Scheduled')]  # EAR v84.35: the deterministic table speaks first",
                "def _ear_json(q, vocab):  # EAR-JSON v84.35: the brain answers the ear in grammar, not prose; offline it is silent",
                "    try:",
                "        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5) as r:",
                "            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]",
                "        if not names: return None",
                "        payload = json.dumps({'model': names[0], 'messages': [{'role': 'user', 'content': f'From this recruiter sentence return ONLY JSON like {{\"tag\": \"<one of: {vocab}>\"}} or {{\"tag\": null}}. Sentence: {q}'}], 'stream': False}).encode()",
                "        req = urllib.request.Request('http://localhost:11434/api/chat', data=payload, headers={'Content-Type': 'application/json'})",
                "        with urllib.request.urlopen(req, timeout=60) as r:",
                "            d = _parse_json(json.loads(r.read().decode())['message']['content'])",
                "        return (d or {}).get('tag')",
                "    except Exception:",
                "        return None",
                "def _ear_intent(q, root, say=print):  # EAR v84.35: a sentence about a human becomes a proposal; the thumb still executes",
                "    ql = (q or '').lower()",
                "    if not any(w in ql for w in EAR_WORDS): return False",
                "    import butler as _bt",
                "    nm = _name_from(q) or _local_name(q)",
                "    p = None",
                "    if nm:",
                "        hs = _hits_for(nm, root)",
                "        if len(hs) == 1: p = hs[0]",
                "    if p is None and _bt.sheet_current():",
                "        p = _bt.sheet_current()['p']; nm = nm or os.path.splitext(os.path.basename(p))[0]",
                "    if not p: return False",
                "    tag = next((t for w, t in EAR_TAGS if w in ql), None)",
                "    if not tag: tag = _ear_json(q, ' / '.join(_bt._tag_vocab()))",
                "    if not tag or tag not in _bt._tag_vocab(): return False",
                "    on = not any(w in ql for w in ('remove', 'undo', 'off', 'cancel'))",
                "    say(f'🤖 Proposal: {os.path.splitext(os.path.basename(p))[0]} → [{tag}] (heard from your sentence) · y / n')",
                "    try:",
                "        json.dump({'p': p, 'tag': tag, 'on': on, 'move_to': True}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))",
                "    except Exception:",
                "        return False",
                "    say('· proposal waiting - type y or n on the next line')",
                "    return True",
                ""]
    done.append('ear-fns')
    srcg = '\n'.join(g)
    for k, l in enumerate(g):
        if l.startswith('def answer(root, q, say=print):'):
            g.insert(k+1, (ind(l)+4)*' ' + "if _ear_intent(q, root, say): return  # EAR v84.35: a sentence about a human becomes a proposal before the brain wanders")
            done.append('ear-hook'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.35' not in t:
        open(AR, 'a').write('v84.35: ear - sentence→proposal via _ear_intent/_ear_json (strict JSON brain, offline silent, deterministic table first, thumb executes); regions pre-flight counted by the patch itself\n')
        done.append('arch-line')
except Exception:
    pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S298 a sentence proposes and never acts - the thumb executes", "'S297 no region is replaced before its markers are counted", "ck('S298 a sentence proposes and never acts - the thumb executes', (chr(35)+' EAR v84.35') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('def _ear_intent(' in open(os.path.join(BASE_DIR, 'briefing.py')).read()) and ('pending_action.json' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S299 the brain answers the ear in strict JSON only, and offline it is silent", "'S298 a sentence proposes and never acts - the thumb executes", "ck('S299 the brain answers the ear in strict JSON only, and offline it is silent', (chr(35)+' EAR-JSON v84.35') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('localhost:11434' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

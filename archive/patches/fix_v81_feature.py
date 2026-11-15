import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
F = open('briefing.py').read().split('\n')
i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_missed('))
j = next(k for k in range(i+1, len(F)) if F[k].strip().startswith('def '))
seg = F[i:j]
n0 = sum("_tpl_for(['missed'])" in l for l in seg)
if n0:
    F[i:j] = [l.replace("_tpl_for(['missed'])", "_tpl_for(words or ['missed'])") for l in seg]
    done.append(f'missed-honors-words-x{n0}')
if 'def _stage_words(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_missed('))
    F[i:i] = ["def _stage_words(who):",
              "    import ledger",
              "    nm = os.path.splitext(os.path.basename(who))[0].lower() if str(who).lower().endswith('.pdf') else re.sub(r'[^a-z]', ' ', str(who).lower()).strip()",
              "    cs = ledger._load(ledger.CASES).get(nm.replace(' ', ''), {}) or ledger._load(ledger.CASES).get(nm, {})",
              "    sts = cs.get('stages') or []",
              "    st = (sts[0].get('stage') or '').lower() if sts else ''",
              "    if not st: return None",
              "    if 'rejected' in st or 'closed' in st: return ['rejected']",
              "    if 'awaiting jd' in st: return ['awaiting']",
              "    if 'interview' in st and 'cleared' not in st: return ['interview']",
              "    if 'cleared' in st or 'join' in st or 'payment' in st: return ['feedback']",
              "    if 'feedback pending' in st or 'ready for manager' in st or 'awaiting cv' in st: return ['outbox']",
              "    if 'call scheduled' in st: return ['missed']",
              "    return None",
              "def _tpl_name(words):",
              "    words = words or ['missed']",
              "    try:",
              "        for f in sorted(os.listdir(TPL_DIR)):",
              "            stem = os.path.splitext(f)[0].lower()",
              "            if any(w in stem or stem in w for w in words): return stem",
              "    except Exception: pass",
              "    return 'awaiting (fallback)'",
              ""]
    done.append('stage-words-helper')
i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_missed('))
j = next(k for k in range(i, min(i+90, len(F))) if F[k].strip().startswith('phone = _pick_phone(_phones_by_basename(hit)'))
F[j:j] = [ind(F[j])*' ' + "if words == 'AUTO': words = _stage_words(hit) or ['outbox']",
          ind(F[j])*' ' + "elif words: words = _stage_words(hit) or words",
          ind(F[j])*' ' + "say(f'   🗣 voice: {_tpl_name(words)}')"]
done.append('stage-aware-voices')
for k, l in enumerate(F):
    if "'clientname')" in l and "'follow'" not in l:
        F[k] = l.replace("'clientname')", "'clientname','follow')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'clientname'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'follow': do_missed(arg, root, print, words='AUTO')")
        done.append('cli-follow'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('clientname ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('follow '): do_missed(q[7:].strip(), root, words='AUTO'); continue")
        done.append('chat-follow'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
print('stage briefing', done, flush=True)
B = open('butler.py').read().split('\n')
if "'S60 stage-aware follow" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S59 nudge speaks awaiting voice" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S60 stage-aware follow', 'def _stage_words(' in _br and \"cmd == 'follow'\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S60-guard')
print('✅', done)

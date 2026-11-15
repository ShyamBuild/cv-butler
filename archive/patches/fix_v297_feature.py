import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
c0 = next(k for k, l in enumerate(B) if l.startswith('def _covered_names('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def '))
if 'COVERED-WIDE' not in '\n'.join(B[c0:c1]):
    B[c0:c1] = ["def _covered_names(root):  # COVERED-WIDE v84.16: five signals of already-spoken-to - memory, any tag, the stage folder he rests in, the sheet's closed rows, the stage log",
                "    keys = set(covered_load())",
                "    try:",
                "        for it in sheet_load().get('items', []):",
                "            if it.get('status') != 'waiting' and it.get('p'): keys.add(_name_key(os.path.basename(it['p'])))",
                "    except Exception: pass",
                "    try:",
                "        lg = json.load(open(os.path.join(BASE_DIR, 'stage_log.json')))",
                "        for e in lg[-400:]:",
                "            if e.get('file'): keys.add(_name_key(e['file']))",
                "    except Exception: pass",
                "    seen = set()",
                "    for sc in desk_paths() or [root]:",
                "        for dp, dn, fn in os.walk(sc):",
                "            for x in fn:",
                "                if not _is_desk_candidate(x): continue",
                "                q = os.path.join(dp, x); rq = os.path.realpath(q)",
                "                if rq in seen: continue",
                "                seen.add(rq)",
                "                if _tags_of(q) or os.path.basename(dp) in _tag_vocab(): keys.add(_name_key(x))",
                "    return keys",
                ""]
    done.append('covered-wide')
src = '\n'.join(B)
if 'def _draft_text(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _chair_draft('))
    B[i:i] = ["DRAFTS_DIR = os.path.join(BASE_DIR, 'drafts')  # TEMPLATES v84.16: the master's own wording, read live at the moment of writing",
              "def _sig():",
              "    try: return open(os.path.join(BASE_DIR, 'signature.txt')).read().strip()",
              "    except Exception: return 'Regards,' + chr(10) + 'Sundeep Rana'",
              "def _draft_fields(name, pos, p=None):",
              "    import collections",
              "    meta = {}",
              "    try: meta = json.load(open(os.path.join(BASE_DIR, 'desk_meta.json'))).get(desk_load().get('primary') or '', {})",
              "    except Exception: pass",
              "    role, loc = (pos.split(' -', 1) + [''])[:2] if pos else ('', '')",
              "    full = name",
              "    if p:",
              "        try:",
              "            v = get_visual_name(p)",
              "            if v: full = v",
              "        except Exception: pass",
              "    return collections.defaultdict(str, {'first': (full or name).split()[0].title(), 'full': (full or name).title(), 'role': role.strip(), 'company': meta.get('company', ''), 'loc': loc.strip(), 'pos': pos or '', 'signature': _sig()})",
              "def _draft_text(kind, name, pos, p=None):",
              "    lp = os.path.join(DRAFTS_DIR, kind + '.txt')",
              "    if not os.path.exists(lp): return None",
              "    try: return open(lp).read().strip().format_map(_draft_fields(name, pos, p))",
              "    except Exception: return None",
              "def meta_cmd(arg, root, say=print):  # TEMPLATES v84.16: teach the company once per desk",
              "    d = desk_load()",
              "    if not d.get('primary'): say('🤷 no desk seated - seat one first'); return",
              "    try: m = json.load(open(os.path.join(BASE_DIR, 'desk_meta.json')))",
              "    except Exception: m = {}",
              "    m[d['primary']] = {'company': arg.strip()}",
              "    json.dump(m, open(os.path.join(BASE_DIR, 'desk_meta.json'), 'w'), indent=1)",
              "    say(f'🏢 company for this desk: {arg.strip()}')",
              ""]
    done.append('templates')
    src = '\n'.join(B)
d0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_draft('))
d1 = next(k for k in range(d0 + 1, len(B)) if B[k].startswith('def '))
if '_draft_text(' not in '\n'.join(B[d0:d1]):
    B[d0:d1] = ["def _chair_draft(kind, name, pos, p=None):  # DRAFTS v84.11 (v84.16): the master's templates first, the house's defaults second, his signature always",
                "    t = _draft_text(kind, name, pos, p)",
                "    if t: return t",
                "    first = (name or '').split()[0].title()",
                "    if kind == 'jd': base = f'Hi {first}, great speaking with you today. I have shared the JD for {pos} on your email - please go through it and confirm your interest so I can move your profile forward.'",
                "    elif kind == 'cv': base = f'Hi {first}, as discussed on call, please share your updated CV at the earliest so I can push your profile to the manager today.'",
                "    elif kind == 'refer': base = f'Hi {first}, thank you for your time today. I have noted you are not keen on this role - if any friend or colleague might fit, do refer them to me. Wishing you the very best.'",
                "    elif kind == 'missed': base = f'Hi {first}, I tried reaching you just now about your application - whenever you are free, please call me back or tell me a good time to connect.'",
                "    else: base = None",
                "    return (base + chr(10) + _sig()) if base else None",
                ""]
    done.append('chair-draft-templates')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if '_chair_draft(draft, cur[' in l and ', p)' not in l:
        B[k] = l.replace("_chair_draft(draft, cur['name'], pos)", "_chair_draft(draft, cur['name'], pos, p)")
        done.append('draft-call-p'); break
src = '\n'.join(B)
h0 = next(k for k, l in enumerate(B) if l.startswith('def _chase_draft('))
h1 = next(k for k in range(h0 + 1, len(B)) if B[k].startswith('def '))
if '_draft_text(' not in '\n'.join(B[h0:h1]):
    B[h0:h1] = ["def _chase_draft(p, tag):  # CHASE v84.0 (v84.16): the background chase speaks in the master's templates too",
                "    name = os.path.splitext(os.path.basename(p))[0]",
                "    parts = p.split(os.sep)",
                "    pos = parts[-2] if len(parts) >= 2 else ''",
                "    kind = 'jd' if tag == 'Awaiting JD Confirmation' else 'cv'",
                "    t = _draft_text(kind, name, pos, p)",
                "    if t: return t",
                "    return _chair_draft(kind, name, pos, p)",
                ""]
    done.append('chase-templates')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'release', 'forget')" in l and 'meta' not in l:
        B[k] = l.replace("'forget')", "'forget', 'meta')")
        done.append('cli-meta-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'forget':") and 'meta' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "elif _v == 'meta': meta_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-meta-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'meta_cmd' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('forget '):"):
            g.insert(k+1, ind(l)*' ' + "if q.startswith('meta '): butler.meta_cmd(q[5:].strip(), root, say); continue  # TEMPLATES v84.16")
            done.append('chat-meta'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S268 coverage reads five signals, not one", "'S267 a proposal survives Enter and waits for a typed answer", "ck('S268 coverage reads five signals, not one', (chr(35)+' COVERED-WIDE v84.16') in _src)"),
      ("'S269 every draft is composed from the master's templates, read live", "'S268 coverage reads five signals, not one", "ck('S269 every draft is composed from the master'+chr(39)+'s templates, read live', (chr(35)+' TEMPLATES v84.16') in _src and ('def _draft_text(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
BLOCK = [("SKIPS_PATH =", ["SKIPS_PATH = os.path.join(BASE_DIR, 'skips.json')  # SKIP v84.11: today's list, not today's verdicts"]),
         ("def skips_load(", ["def skips_load():",
                              "    try: return json.load(open(SKIPS_PATH))",
                              "    except Exception: return {}"]),
         ("def _fp(", ["def _fp(p):  # FP v84.11: size plus a head-crc - a rename cannot change either",
                       "    import zlib",
                       "    try:",
                       "        st = os.stat(p)",
                       "        with open(p, 'rb') as f: head = f.read(65536)",
                       "        return [st.st_size, zlib.crc32(head)]",
                       "    except Exception:",
                       "        return None"]),
         ("def _find_by_fp(", ["def _find_by_fp(fp, root):",
                               "    if not fp: return None",
                               "    for sc in desk_paths() or [root]:",
                               "        for dp, dn, fn in os.walk(sc):",
                               "            for x in fn:",
                               "                q = os.path.join(dp, x)",
                               "                if _fp(q) == fp: return q",
                               "    return None"]),
         ("def unskip_cmd(", ["def unskip_cmd(arg, root, say=print):  # SKIP v84.11",
                              "    sk = skips_load(); hit = [k for k in sk if arg and arg.lower() in os.path.basename(k).lower()]",
                              "    if not hit: say(f'🤷 no skipped candidate matches {arg!r}'); return",
                              "    for k in hit: sk.pop(k, None)",
                              "    json.dump(sk, open(SKIPS_PATH, 'w'), indent=1)",
                              "    say('↩️ unskipped: ' + ', '.join(os.path.basename(k) for k in hit) + ' - the next calls will seat them again')"]),
         ("def followup_cmd(", ["def followup_cmd(arg, root, say=print):  # FOLLOWUP v84.11: the debts, by name, not by count",
                                "    seen = set(); jd = []; cv = []",
                                "    for sc in desk_paths():",
                                "        for dp, dn, fn in os.walk(sc):",
                                "            for x in fn:",
                                "                if not _is_desk_candidate(x): continue",
                                "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
                                "                if rp in seen: continue",
                                "                seen.add(rp)",
                                "                tgs = _tags_of(p)",
                                "                if 'Awaiting JD Confirmation' in tgs: jd.append((x, os.path.basename(dp)))",
                                "                if 'Awaiting CV Update' in tgs: cv.append((x, os.path.basename(dp)))",
                                "    say(f'📬 awaiting JD acknowledgement: {len(jd)}')",
                                "    for x, f in jd[:10]: say(f'   · {x} · in {f}')",
                                "    say(f'📬 awaiting CV update: {len(cv)}')",
                                "    for x, f in cv[:10]: say(f'   · {x} · in {f}')",
                                "    due = []",
                                "    try:",
                                "        er = json.load(open(os.path.join(BASE_DIR, 'errands.json')))",
                                "        for p, e in er.items():",
                                "            if isinstance(e, dict) and any(k.endswith(':chased') for k in e): due.append(os.path.basename(p))",
                                "    except Exception: pass",
                                "    if due: say('📨 chase due now: ' + ', '.join(due[:6]) + ' - chase send <name> opens the draft')",
                                "    else: say('📨 no chase due right now')"])]
missing = [lines for marker, lines in BLOCK if marker not in src]
if missing:
    i = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
    flat = []
    for marker, lines in BLOCK:
        if marker not in src: flat += lines + [""]
    B[i:i] = flat
    done.append('skip-repair')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('CHAIR_WORDS =') and 'skip for now' not in l:
        B[k] = l[:l.rstrip().rfind('}')] + ", 'skip for now': '6', 'skip him for now': '6'}"
        done.append('chair-words-phrase'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S270 every name the skip branch speaks is defined in the same book", "'S269 every draft is composed from the master's templates, read live", "ck('S270 every name the skip branch speaks is defined in the same book', ('SKIPS_PATH =' in _src) and ('def skips_load(' in _src) and ('def _fp(' in _src) and ('def outcome_cmd(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

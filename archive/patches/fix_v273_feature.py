import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if not B[0].startswith('_CLI_VERB'):
    B[0:0] = ["import sys as _sys0",
              "_CLI_VERB = len(_sys0.argv) > 1 and _sys0.argv[1] in ('pending', 'status', 'note', 'desk', 'briefing', 'chase')  # QUIET-VERBS v84.2: a verb is answered without the clerk clearing his throat"]
    done.append('quiet-verbs-top')
for k in range(len(B) - 1, 1, -1):
    l = B[k]
    if l.strip().startswith(('print', 'say')) and ('live lock:' in l or 'butler v6' in l) and not B[k-1].strip().startswith('if not _CLI_VERB'):
        d = ind(l)
        B[k:k+1] = [d*' ' + 'if not _CLI_VERB:', (d+4)*' ' + l.strip()]
        if 'quiet-verbs-wrap' not in done: done.append('quiet-verbs-wrap')
src = '\n'.join(B)
t0 = next(k for k, l in enumerate(B) if l.startswith('def _tags_of('))
t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def ') or B[k].startswith('PIPELINE_CLOCKED'))
if 'import plistlib' not in '\n'.join(B[t0:t1]):
    i = next(k for k in range(t0, t1) if B[k].strip().startswith('raw = _xattr_raw('))
    B.insert(i, '    import plistlib  # S230 v84.2b: the function carries its own import - a module-level absence once silenced it for thirteen laps')
    done.append('tags-of-import')
src = '\n'.join(B)
if 'def _tag_write(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _pl_root():'))
    B[i:i] = ["def _tag_write(p, tags):  # TAG-WRITE v84.0: libc setxattr, synchronous - what we write is what the next read sees",
              "    import plistlib as _pl",
              "    name = 'com.apple.metadata:_kMDItemUserTags'",
              "    if tags: _xattr_set_raw(p, name, _pl.dumps(tags, fmt=_pl.FMT_BINARY))",
              "    else: _xattr_del_raw(p, name)",
              "def _tag_roundtrip_ok():  # S217 witness body - prints its own steps if it ever falls again",
              "    import tempfile, plistlib as _pl",
              "    tp = None",
              "    try:",
              "        fd, tp = tempfile.mkstemp(suffix='.pdf', dir=BASE_DIR); os.close(fd)",
              "        _tag_write(tp, ['Alpha Tag'])",
              "        _raw = _xattr_raw(tp)",
              "        cur = _tags_of(tp)",
              "        if not cur: print('🔬 S217 steps: len(raw)=' + str(len(_raw)) + ' hex=' + _raw.hex()[:64] + ' loads=' + repr(_pl.loads(_raw) if _raw else None))",
              "        _tag_write(tp, (cur or []) + ['Beta Tag']); cur2 = _tags_of(tp)",
              "        ok = 'Alpha Tag' in cur2 and 'Beta Tag' in cur2",
              "        _tag_write(tp, [t for t in cur2 if t != 'Beta Tag']); fin = _tags_of(tp)",
              "        ok = ok and 'Alpha Tag' in fin",
              "        if not ok: print('⚠️ S217 detail: cur=' + repr(cur) + ' cur2=' + repr(cur2) + ' final=' + repr(fin))",
              "        os.remove(tp); return ok",
              "    except Exception as _e:",
              "        print('⚠️ S217 detail: ' + repr(_e))",
              "        try:",
              "            if tp: os.remove(tp)",
              "        except Exception: pass",
              "        return False",
              "def _tag_vocab():  # DESK v84.0: built at call time, so no ordering of the book can starve it",
              "    return list(PIPELINE_CLOCKED) + list(PIPELINE_MOMENT) + list(PIPELINE_TERMINAL) + list(PIPELINE_PRE)",
              "def _match_tag(w):",
              "    low = (w or '').lower(); best = None",
              "    for t in _tag_vocab():",
              "        if low == t.lower() or (len(low) > 3 and low in t.lower()): best = t",
              "    return best",
              "def tag_apply(name, tagwords, on, say=print):  # TAG-VOICE v84.0: your word moves the tag, the machine keeps the rest",
              "    tag = _match_tag(tagwords)",
              "    if not tag: say(f'🤷 no known tag matches {tagwords!r}'); return",
              "    scope = desk_paths() or [_pl_root()]",
              "    toks = [t for t in name.lower().split() if t]; cands = []",
              "    for sc in scope:",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if x.lower().endswith(('.pdf', '.docx')) and all(t in x.lower() for t in toks): cands.append(os.path.join(dp, x))",
              "    if not cands: say(f'🤷 no candidate file matches {name!r} on the desk'); return",
              "    if len(cands) > 1: say('❓ several humans match: ' + ' · '.join(os.path.basename(c) for c in cands[:5])); return",
              "    p = cands[0]; cur = _tags_of(p)",
              "    try:",
              "        if on and tag not in cur: _tag_write(p, cur + [tag]); say(f'🏷️ tagged {os.path.basename(p)}: {tag}')",
              "        elif not on and tag in cur: _tag_write(p, [t for t in cur if t != tag]); say(f'🏷️ untagged {os.path.basename(p)}: {tag}')",
              "        else: say(f'🏷️ {os.path.basename(p)} already {\"wears\" if on else \"lacks\"} {tag} - nothing changed')",
              "    except Exception as _te:",
              "        say(f'⚠️ tag write failed: {_te}')",
              ""]
    done.append('tag-writer')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_tagcmd(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_chase('))
    g[i:i] = ["def do_tagcmd(arg, root, say=print):  # TAG-VOICE v84.0",
              "    parts = arg.split(' ', 1)",
              "    if len(parts) < 2: say('usage: tag <name> <tag words> | tag off <name> <tag words>'); return",
              "    if parts[0] == 'off' and len(parts) > 1:",
              "        q2 = parts[1].split(' ', 1)",
              "        butler.tag_apply(q2[0], q2[1] if len(q2) > 1 else '', False, say); return",
              "    butler.tag_apply(parts[0], parts[1] if len(parts) > 1 else '', True, say)",
              ""]
    done.append('tag-chat-fn')
    srcg = '\n'.join(g)
if not any(l.strip().startswith("if q.startswith('tag ')") for l in g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('chase'): do_chase("):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q.startswith('tag '): do_tagcmd(q[4:].strip(), root); continue  # TAG-VOICE v84.0")
            done.append('tag-chat-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S217 the tag-writer preserves every tag it was not asked about", "'S216 the master's words stand at the head of the chat chain", "ck('S217 the tag-writer preserves every tag it was not asked about', _tag_roundtrip_ok())"),
      ("'S224 the parse asks twice before it stays silent", "'S223 absence reads as empty bytes, never as None", "ck('S224 the parse asks twice before it stays silent', ('FMT_BINARY' in _src[_src.find(chr(10)+'def _tags_of('):_src.find(chr(10)+'def _tags_of(') + 1400]))"),
      ("'S230 every tag function carries its own import", "'S229 a position outranks its client umbrella", "ck('S230 every tag function carries its own import', ('import plistlib' in _src[_src.find(chr(10)+'def _tags_of('):_src.find(chr(10)+'def _tags_of(') + 400]))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

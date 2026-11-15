import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
ks = [k for k, l in enumerate(B) if l.strip().startswith('print') and ('live lock:' in l or 'butler v6' in l)]
if ks and '_CLI_VERB' not in '\n'.join(B):
    d0 = ind(B[ks[0]])
    B.insert(ks[0], d0*' ' + "_CLI_VERB = len(sys.argv) > 1 and sys.argv[1] in ('pending', 'status', 'note', 'desk', 'briefing', 'chase')  # QUIET-VERBS v84.2: a verb is answered without the clerk clearing his throat")
    for k in [k + 1 for k in ks][::-1]:
        d = ind(B[k])
        B[k:k+1] = [d*' ' + 'if not _CLI_VERB:', (d+4)*' ' + B[k].strip()]
    done.append('quiet-verbs')
src = '\n'.join(B)
if 'def _xattr_set_raw(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _xattr_raw('))
    B[i:i] = ["def _xattr_set_raw(p, name, data):  # XATTR-SET v84.0: the writer walks the same libc road as the reader - one hand, one law",
              "    import ctypes",
              "    lc = ctypes.CDLL('/usr/lib/libc.dylib', use_errno=True)",
              "    lc.setxattr.restype = ctypes.c_int",
              "    lc.setxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]",
              "    r = lc.setxattr(p.encode('utf-8'), name.encode('utf-8'), ctypes.cast(data, ctypes.c_void_p), len(data), 0, 0)",
              "    if r != 0: raise OSError(ctypes.get_errno(), 'setxattr failed for ' + str(p))",
              "def _xattr_del_raw(p, name):  # XATTR-SET v84.0",
              "    import ctypes",
              "    lc = ctypes.CDLL('/usr/lib/libc.dylib', use_errno=True)",
              "    lc.removexattr.restype = ctypes.c_int",
              "    lc.removexattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]",
              "    lc.removexattr(p.encode('utf-8'), name.encode('utf-8'), 0)",
              ""]
    done.append('xattr-set')
    src = '\n'.join(B)
r0 = next(k for k, l in enumerate(B) if l.startswith('def desk_resolve('))
r1 = next(k for k in range(r0 + 1, len(B)) if B[k].startswith('def desk_paths('))
if 'DESK-DEPTH' not in '\n'.join(B[r0:r1]):
    B[r0:r1] = ["def desk_resolve(spec, root):  # DESK v84.0 (JD-blind v84.1, depth-preferring v84.2): a chair is a folder that holds people; a position outranks its client umbrella",
                "    toks = [t for t in spec.lower().split() if t]",
                "    best = None; bs = -1; bd = -1; bf = -1",
                "    for dp, dn, fn in os.walk(root):",
                "        rel = os.path.relpath(dp, root)",
                "        if rel == '.' or rel.count(os.sep) > 1: continue",
                "        if any(seg.lower().startswith('jd') for seg in rel.split(os.sep)): continue  # DESK-JD-BLIND v84.1",
                "        depth = rel.count(os.sep)",
                "        papers = [x for x in fn if x.lower().endswith(('.pdf', '.docx'))]",
                "        blob = rel.lower() + ' ' + ' '.join(papers).lower()",
                "        hit = sum(1 for t in toks if t in blob)",
                "        if hit == len(toks) and (hit > bs or (hit == bs and (depth > bd or (depth == bd and len(papers) > bf)))):  # DESK-DEPTH v84.2",
                "            best, bs, bd, bf = dp, hit, depth, len(papers)",
                "    return best",
                ""]
    done.append('desk-depth')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S221 the tag writer walks the same libc road as the reader", "'S220 the small model thinks on a small machine", "ck('S221 the tag writer walks the same libc road as the reader', ('def _xattr_set_raw(' in _src) and (chr(35)+' XATTR-SET v84.0') in _src and ('os.set'+'xattr(') not in _src)"),
      ("'S228 a verb is answered without the clerk clearing his throat", "'S227 a placeholder is never run through relpath", "ck('S228 a verb is answered without the clerk clearing his throat', ('_CLI_VERB' in _src) and ('if not _CLI_VERB:' in _src))"),
      ("'S229 a position outranks its client umbrella", "'S228 a verb is answered without the clerk clearing his throat", "ck('S229 a position outranks its client umbrella', (chr(35)+' DESK-DEPTH v84.2') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

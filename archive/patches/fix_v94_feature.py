import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _has_tag_xattr(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _tags_from_plist('))
    B[i:i] = ["def _tags_of_fast(p):",
              "    try:",
              "        import plistlib",
              "        arr = plistlib.loads(os.getxattr(p, 'com.apple.metadata:_kMDItemUserTags'))",
              "        out = [str(t).split(chr(10))[0].strip() for t in arr]",
              "        return [t for t in out if t and t not in COLOR_TAGS]",
              "    except Exception:",
              "        return None",
              "def _has_tag_xattr(p):",
              "    t = _tags_of_fast(p)",
              "    if t is None: return False",
              "    return any(x in TAG_NAMES or x.replace(chr(8211), '-') in TAG_NAMES for x in t)",
              ""]
    done.append('fast-xattr-tag-read')
src = '\n'.join(B)
if '# TAGS-FIRST v63' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'p = self.normalize_suffix(p, say)' and k > next(j for j, l2 in enumerate(B) if l2.strip() == 'elif ext == \'.pdf\':'))
    B.insert(i, ind(B[i])*' ' + "if _has_tag_xattr(p): p = self.handle_tags(p, say) or p  # TAGS-FIRST v63")
    done.append('tags-first')
if 'return dst' not in '\n'.join(B)[next(k for k, l in enumerate(B) if l.strip().startswith('def handle_tags(')):]:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def handle_tags('))
    j = next(k for k in range(i, i+40) if '[move]' in B[k])
    B.insert(j+1, ind(B[j])*' ' + "return dst")
    done.append('handle-tags-returns-path')
src = '\n'.join(B)
if '_tags_of_fast(p) or get_tags(p)' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def handle_tags('))
    j = next(k for k in range(i, i+12) if B[k].strip() == 'T = get_tags(p)')
    B[j] = ind(B[j])*' ' + 'T = _tags_of_fast(p) or get_tags(p)'
    done.append('handle-tags-fast-path')
src = '\n'.join(B)
if 'B.journal.get(p) == _jk' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def work(p, total=0):'))
    j = next(k for k in range(i, i+12) if B[k].strip() == 'B.route(p, print)')
    k0 = j - 1
    B[k0:k0] = [ind(B[k0])*' ' + "try:",
                ind(B[k0])*' ' + "    if not hasattr(B, 'journal'): B._jload()",
                ind(B[k0])*' ' + "    _jk = B._jkey(p)",
                ind(B[k0])*' ' + "    if _jk and B.journal.get(p) == _jk: return  # WORK-DOOR SKIP v63",
                ind(B[k0])*' ' + "except Exception: pass"]
    done.append('work-door-journal-skip')
if 'B._jload()' not in src or 'work-door' not in src:
    pass
src = '\n'.join(B)
if "\n    B._jload()\n" not in src and 'B = Butler(root)' in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'B = Butler(root)')
    B.insert(i+1, ind(B[i])*' ' + 'B._jload()')
    done.append('boot-journal-load')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S73 tags-first filing" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S72 settle-fast + pending drain" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S73 tags-first filing', 'def _has_tag_xattr(' in _src and (chr(35)+' TAGS-FIRST') in _src and 'def _tags_of_fast(' in _src)")
    B.insert(i+2, d*' ' + "ck('S74 worker-door journal skip', (chr(35)+' WORK-DOOR SKIP') in _src and 'B._jload()' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S73-S74-guards')
print('✅', done)

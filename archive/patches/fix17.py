import ast
p = 'briefing.py'; L = open(p).read().split('\n')

# Fix: normalize spaces to underscores in folder name comparison
for i, l in enumerate(L):
    if 'top_folder = rel.split(os.sep)[0].lower().replace' in l and "'\\u2013', '-')" in l:
        d = len(l) - len(l.lstrip())
        L[i] = d*' ' + "top_folder = rel.split(os.sep)[0].lower().replace('\\u2013', '-').replace(' ', '_')"
        print('fixed folder normalization (spaces -> underscores)')
        break

# Also fix tag_keys to use the same normalization
for i, l in enumerate(L):
    if "tag_keys = {k.lower().replace('\\u2013', '-')" in l and "' ', '_')" not in l:
        d = len(l) - len(l.lstrip())
        L[i] = d*' ' + "tag_keys = {k.lower().replace('\\u2013', '-').replace(' ', '_') for k, _, _ in TAGS}"
        print('fixed tag_keys normalization')
        break

# Clear the tags cache so stale entries are flushed
import os
cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tags_cache.json')
if os.path.exists(cache):
    os.remove(cache)
    print('cleared tags_cache.json')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('done')

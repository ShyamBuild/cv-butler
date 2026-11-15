import ast

# 1) Fix briefing.py: define BASE_DIR if missing, and make TAGS_CACHE robust
p = 'briefing.py'; L = open(p).read().split('\n')

# Add BASE_DIR near the top if not present
if not any(l.strip().startswith('BASE_DIR =') for l in L[:30]):
    # Insert after the first import block
    for i, l in enumerate(L):
        if l.strip().startswith('import ') and not l.strip().startswith('import '):
            pass
        if l.strip() == 'import re' or l.strip().startswith('import '):
            if i+1 < len(L) and not L[i+1].strip().startswith('import '):
                L.insert(i+1, "BASE_DIR = os.path.dirname(os.path.abspath(__file__))")
                print('added BASE_DIR to briefing.py')
                break

# Also fix TAGS_CACHE line to use os.path.dirname if BASE_DIR is still missing
for i, l in enumerate(L):
    if "TAGS_CACHE = os.path.join(BASE_DIR, 'tags_cache.json')" in l:
        if not any(l2.strip().startswith('BASE_DIR =') for l2 in L[:i]):
            L[i] = "TAGS_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tags_cache.json')"
            print('fixed TAGS_CACHE to use __file__')

ast.parse('\n'.join(L)); open(p, 'w').write('\n'.join(L))
print('briefing.py fixed')

# 2) Verify import works
import subprocess
r = subprocess.run(['cv_env/bin/python3', '-c', 'import briefing; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])

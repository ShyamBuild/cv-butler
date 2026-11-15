import ast, subprocess

# 1) Fix briefing.py: ensure BASE_DIR is defined, and add debug
p = 'briefing.py'; L = open(p).read().split('\n')

# Add BASE_DIR if missing
if not any(l.strip().startswith('BASE_DIR =') for l in L[:30]):
    for i, l in enumerate(L):
        if l.strip().startswith('import ') and i+1 < len(L) and not L[i+1].strip().startswith('import '):
            L.insert(i+1, "BASE_DIR = os.path.dirname(os.path.abspath(__file__))")
            print('added BASE_DIR')
            break

# 2) Fix butler.py: ensure handle_tags runs on every sweep (no journal veto for moves)
p = 'butler.py'; L = open(p).read().split('\n')
for i, l in enumerate(L):
    if l.strip() == 'self.handle_tags(pdf, say)' and 'skip_tags' not in l:
        d = len(l) - len(l.lstrip())
        L[i] = d*' ' + "if not getattr(self, '_skip_tags', False): self.handle_tags(pdf, say)"
        print('tags-always-run')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

# 3) Test import and tag reading
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import briefing, os
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai Location/Vaibhav Chaudhary.pdf"
if os.path.exists(p):
    tags = briefing._tags_of(p)
    print("tags on Vaibhav:", tags)
else:
    print("file not found")
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])

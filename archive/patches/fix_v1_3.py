import ast, os, subprocess
ROOT = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
def _n(s): return (s or '').lower().replace('\u2013', '-').replace(' ', '_')
done = []

# 1) ONE-TIME MERGE: keep the OLDEST folder of each twin group, move contents, delete empties
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if not d.startswith('.')]
    groups = {}
    for d in list(dn):
        groups.setdefault(_n(d), []).append(os.path.join(dp, d))
    for key, dirs in groups.items():
        if len(dirs) < 2: continue
        dirs.sort(key=os.path.getctime)
        keep = dirs[0]
        for other in dirs[1:]:
            for f in os.listdir(other):
                src = os.path.join(other, f); dst = os.path.join(keep, f)
                if os.path.exists(dst):
                    b, e = os.path.splitext(f); c = 1
                    while os.path.exists(dst): dst = os.path.join(keep, f"{b}_{c}{e}"); c += 1
                os.rename(src, dst)
                print('merged:', f, '->', os.path.basename(keep))
            try:
                os.rmdir(other); print('removed empty twin:', os.path.basename(other)); done.append('merged:' + key)
            except Exception:
                print('twin not empty, kept:', os.path.basename(other))

# 2) butler.py: RULES_VERSION + existing-folder rule
p = 'butler.py'; L = open(p).read().split('\n')
if not any(l.strip().startswith('RULES_VERSION =') for l in L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'class Butler:')
    L.insert(i+1, "    RULES_VERSION = 'v13-decisions-free'")
    done.append('RULES_VERSION-restored')
HELPER = ["    def _folder_for_tag(self, base, tag):",
          "        def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')",
          "        try:",
          "            for d in os.listdir(base):",
          "                if os.path.isdir(os.path.join(base, d)) and _n(d) == _n(tag):",
          "                    return os.path.join(base, d)",
          "        except Exception:",
          "            pass",
          "        return os.path.join(base, tag)",
          ""]
if not any(l.strip().startswith('def _folder_for_tag(') for l in L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def handle_tags('))
    L[i:i] = HELPER
    done.append('folder-for-tag-helper')
for i, l in enumerate(L):
    if l.strip() == 'target_folder = os.path.join(self.position_folder_for(p), safe_tag)':
        L[i] = '        target_folder = self._folder_for_tag(self.position_folder_for(p), safe_tag)'
        done.append('handle_tags-uses-existing')
    if l.strip() == 'tgt = os.path.join(self.position_folder_for(fp), tag)':
        L[i] = '                tgt = self._folder_for_tag(self.position_folder_for(fp), tag)'
        done.append('reconcile-uses-existing')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)

# 3) SELFTEST GATE (visible errors this time)
r = subprocess.run(['cv_env/bin/python3', 'butler.py', '--selftest', ROOT],
                   capture_output=True, text=True, cwd='.')
print((r.stdout + r.stderr).strip()[-800:])

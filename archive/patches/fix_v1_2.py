import ast, re, subprocess
def find_block(L, pat):
    for i, l in enumerate(L):
        m = re.match(r'(\s*)def ' + pat + r'\(', l)
        if m:
            d = len(m.group(1)); j = i + 1
            while j < len(L):
                s = L[j]
                if s.strip() and (len(s) - len(s.lstrip())) <= d: break
                j += 1
            return i, j, d
    return None
done = []
UNESCAPE = [
 'def _unescape(s):',
 '    BS = chr(92) + chr(92)',
 "    s = re.sub(BS + 'U([0-9a-fA-F]{4,8})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = re.sub(BS + 'u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = s.replace(chr(92) + '\"', '\"')",
 '    return s',
]
ROUTE = [
 '    def route(self, p, say):',
 '        p = os.path.abspath(p)',
 "        if os.path.basename(os.path.dirname(p)).lower() in ('converted doc files', 'converted files', 'duplicates', 'previous versions'):",
 '            return',
 "        if not hasattr(self, 'journal'): self._jload()",
 '        jk = self._jkey(p)',
 '        self._skip_tags = bool(jk and self.journal.get(p) == jk)',
 '        self._no_cache = False',
 '        acted = []',
 '        def wsay(m):',
 '            acted.append(1)',
 '            say(m)',
 "        if p.lower().endswith('.eml'):",
 '            pdf = self.handle_convert(p, wsay)',
 '            if pdf: self.handle_pdf(pdf, wsay)',
 "            if acted and not getattr(self, 'scanning', False):",
 '                say("   👀 back to watching…")',
 '            return',
 '        with self.lock:',
 '            if p in self.busy: return',
 '            self.busy.add(p)',
 '        try:',
 '            self._route(p, wsay)',
 '        finally:',
 '            with self.lock:',
 '                self.busy.discard(p)',
 "            if jk and not getattr(self, '_no_cache', False):",
 '                self.journal[p] = jk',
 '                self._jdirty = True',
 "            if acted and not getattr(self, 'scanning', False):",
 '                say("   👀 back to watching…")',
 '    def _route(self, p, say):',
 "        if p.lower().endswith('.tmp.html'):",
 '            try:',
 '                if time.time() - os.path.getmtime(p) > 600:',
 '                    os.remove(p)',
 '                    say(f"\\n🧹 [clean] removed stale temp: {os.path.basename(p)}")',
 '            except Exception:',
 '                pass',
 '            return',
 '        ext = os.path.splitext(p)[1].lower()',
 "        if ext in ('.doc', '.docx', '.msg'):",
 '            pdf = self.handle_convert(p, say)',
 '            if pdf and os.path.exists(pdf):',
 '                self.handle_pdf(pdf, say)',
 "                if not getattr(self, '_skip_tags', False): self.handle_tags(pdf, say)",
 "        elif ext == '.pdf':",
 '            p = self.normalize_suffix(p, say)',
 '            self.handle_pdf(p, say)',
 "            if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)",
 "        elif ext == '.xlsx':",
 '            self.handle_excel(p, say)',
 "            if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)",
]
# ---- butler.py ----
p = 'butler.py'; L = open(p).read().split('\n')
b = find_block(L, '_unescape')
if b: L[b[0]:b[1]] = UNESCAPE; done.append('butler _unescape double-backslash')
if not any(re.match(r'\s*def route\(', l) for l in L):
    k = next(i for i, l in enumerate(L) if l.strip().startswith('def handle_tags(') or l.startswith('def main('))
    L[k:k] = ROUTE + ['']; done.append('route+_route inserted')
out = []
for i, l in enumerate(L):
    if l.strip() == 'self._reconcile_tags(say)' and i+1 < len(L) and L[i+1].strip() == 'self._reconcile_tags(say)':
        out.append(l); continue
    if l.strip() == 'self._reconcile_tags(say)' and out and out[-1].strip() == 'self._reconcile_tags(say)':
        continue
    out.append(l)
L = out; done.append('reconcile-call deduped')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
# ---- briefing.py ----
p = 'briefing.py'; L = open(p).read().split('\n')
b = find_block(L, '_unescape')
if b: L[b[0]:b[1]] = UNESCAPE; done.append('briefing _unescape double-backslash')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)
r = subprocess.run(['cv_env/bin/python3', 'butler.py', '--selftest',
                    '/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location'],
                   capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip()[-500:])

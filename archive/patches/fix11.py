import ast
def ind(l): return len(l) - len(l.lstrip())

p = 'butler.py'; L = open(p).read().split('\n'); done = []
if 'atexit.register' not in '\n'.join(L):
    for i, l in enumerate(L):
        if l.strip() == 'import briefing':
            d = ind(l)
            L[i+1:i+1] = [d*' ' + 'import atexit', d*' ' + 'def _close_wa_atexit():',
                          d*' ' + '    try:', d*' ' + '        import wa; wa.close()',
                          d*' ' + '    except Exception:', d*' ' + '        pass',
                          d*' ' + 'atexit.register(_close_wa_atexit)']
            done.append('atexit-wa'); break
if 'named = [t for t in T if t in TAG_NAMES]' not in '\n'.join(L):
    for i, l in enumerate(L):
        if l.strip() == 'T = get_tags(p)' and i+1 < len(L) and L[i+1].strip() == 'if len(T) != 1: return':
            d = ind(l)
            L[i:i+3] = [d*' ' + 'T = get_tags(p)',
                        d*' ' + 'named = [t for t in T if t in TAG_NAMES]',
                        d*' ' + 'cmap = {}',
                        d*' ' + "try: cmap = json.load(open(os.path.join(BASE_DIR, 'color_tags.json')))",
                        d*' ' + 'except Exception: cmap = {}',
                        d*' ' + 'if len(named) == 1:',
                        d*' ' + '    tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', named[0]).strip()',
                        d*' ' + 'elif not named and len(T) == 1 and T[0] in COLOR_TAGS and cmap.get(T[0]):',
                        d*' ' + '    tag = cmap[T[0]]',
                        d*' ' + 'else:',
                        d*' ' + '    return',
                        d*' ' + 'if not tag: return']
            done.append('tags-named+color'); break
if "line.startswith('tags ')" not in '\n'.join(L):
    for i, l in enumerate(L):
        if l.strip() == "elif line in ('status', 's'):":
            d = ind(l)
            L[i:i] = [d*' ' + "elif line.startswith('tags '):",
                      d*' ' + "    hits = briefing._hits_for(line[5:], root)",
                      d*' ' + '    if not hits: print("no match")',
                      d*' ' + '    else:',
                      d*' ' + '        for h in hits[:3]: print("tags:", os.path.basename(h), get_tags(h) or "(none)")']
            done.append('console-tags'); break
for i, l in enumerate(L):
    if l.strip() == 'os._exit(0)' and 'wa.close()' not in '\n'.join(L[max(0,i-3):i]):
        d = ind(l); L[i:i] = [d*' ' + 'try: import wa; wa.close()', d*' ' + 'except Exception: pass']
        done.append('wa-close-exit')
    if l.strip().startswith('os.execv(sys.executable,') and 'wa.close()' not in L[i-1]:
        d = ind(l); L[i:i] = [d*' ' + 'try: import wa; wa.close()', d*' ' + 'except Exception: pass']
        done.append('wa-close-restart')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('butler:', done or 'nothing missing')

p = 'briefing.py'; L = open(p).read().split('\n'); done = []
if not any(l.strip().startswith('("awaiting jd confirmation"') for l in L):
    for i, l in enumerate(L):
        if 'awaiting cv update' in l and 'CV UPDATE' in l:
            d = ind(l)
            L[i+1:i+1] = [d*' ' + '("awaiting jd confirmation", " JD SHARED - ACK PENDING", "acknowledgement awaited"),',
                          d*' ' + '("interview cleared",        "🎉 INTERVIEW CLEARED", "next round / offer"),',
                          d*' ' + '("expected to join",         "🚪 EXPECTED TO JOIN", "onboarding follow-up"),',
                          d*' ' + '("joined - payment pending", "💰 JOINED - PAYMENT PENDING", "invoice follow-up"),',
                          d*' ' + '("payment received",         "✅ PAYMENT RECEIVED", ""),',
                          d*' ' + '("closed - not proceeding",  "🚫 CLOSED - NOT PROCEEDING", ""),',
                          d*' ' + '("rejected by client",       "❌ REJECTED BY CLIENT", ""),']
            done.append('tag-board'); break
for i, l in enumerate(L):
    if l.strip() == 't = os.path.basename(dp).lower()' and '.replace' not in l:
        d = ind(l); L[i] = d*' ' + "t = os.path.basename(dp).lower().replace('\\u2013', '-')"
        done.append('dash-normalize')
if "if 'jd' in q or 'ack' in q" not in '\n'.join(L):
    for i, l in enumerate(L):
        if l.strip().startswith("return {'tags': tags or"):
            d = ind(l)
            L[i:i] = [d*' ' + "if 'jd' in q or 'ack' in q: tags.append('awaiting jd confirmation')",
                      d*' ' + "if 'cleared' in q: tags.append('interview cleared')",
                      d*' ' + "if 'join' in q: tags.append('expected to join')",
                      d*' ' + "if 'payment' in q: tags += ['joined - payment pending', 'payment received']",
                      d*' ' + "if 'closed' in q or 'reject' in q: tags += ['closed - not proceeding', 'rejected by client']"]
            done.append('router'); break
for i, l in enumerate(L):
    if 'ph[0] if isinstance(ph, list)' in l and "(ph or [''])" not in l:
        d = ind(l); L[i] = d*' ' + "ph = (ph or [''])[0] if isinstance(ph, list) else ph"
        done.append('list-guard')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('briefing:', done or 'nothing missing')

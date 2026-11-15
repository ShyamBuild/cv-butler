import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
n = 0
for k, l in enumerate(B):
    if l.strip() == 'import fitrank' and k+1 < len(B) and 'phones_of(fitrank._text(fp))' in B[k+1]:
        B[k] = None; B[k+1] = ind(B[k+1])*' ' + 'phs = phones_of(fp) or []'; n += 1
    if l.strip() == 'import fitrank as _fr' and k+1 < len(B) and 'phones_of(_fr._text(p))' in B[k+1]:
        B[k] = None; B[k+1] = ind(B[k+1])*' ' + '_phs = phones_of(p) or []'; n += 1
B = [l for l in B if l is not None]
if n: done.append(f'phones-of-path-x{n}')
src = '\n'.join(B)
old_cd = "            if time.time() - lg.get(k, 0) < 86400: return"
if old_cd in src:
    i = next(k for k, l in enumerate(B) if l == old_cd)
    B[i-1] = ind(B[i-1])*' ' + "k = f'{fp}|{tg}'  # 60s debounce per file+tag, replaces 24h cooldown"
    B[i] = ind(B[i])*' ' + "if time.time() - lg.get(k, 0) < 60: return"
    done.append('debounce-replace')
src = '\n'.join(B)
if '# MULTI-NUM v81.19' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'self._ad_fire(d, txt, v, nm, say)')
    d = ind(B[i])
    B.insert(i+1, d*' ' + "for _d2 in phs:  # MULTI-NUM v81.19: every number in the CV gets its own draft")
    B.insert(i+2, d*' ' + "    if _d2 == d: continue")
    B.insert(i+3, d*' ' + "    try: q2 = json.load(open(os.path.join(BASE_DIR, 'autodraft_queue.json')))")
    B.insert(i+4, d*' ' + "    except Exception: q2 = []")
    B.insert(i+5, d*' ' + "    q2 = [x for x in q2 if time.time() - x.get('at', 0) < 7200]")
    B.insert(i+6, d*' ' + "    q2.append({'phone': _d2, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v})")
    B.insert(i+7, d*' ' + "    json.dump(q2, open(os.path.join(BASE_DIR, 'autodraft_queue.json'), 'w'), indent=1)")
    B.insert(i+8, d*' ' + "    say(f'📝 queued autodraft (extra number +{_d2}): {nm}')")
    done.append('multi-num')
src = '\n'.join(B)
if '# RETOUCH v81.19' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if add: self._added_tags[fp] = add')
    d = ind(B[i])
    B.insert(i, d*' ' + "if not add and cur: add = list(cur)  # RETOUCH v81.19: a re-applied tag is an event, even inside one poll window")
    done.append('retouch')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S124 phones read from the path, not from prose" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S123 no ghost clock alias" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S124 phones read from the path, not from prose', 'phones_of(fp)' in _src and ('phones_of(fitrank' + '._text') not in _src and ('phones_of(_fr' + '._text') not in _src)")
    B.insert(i+2, d*' ' + "ck('S125 re-apply and multi-number draft', (chr(35)+' RETOUCH') in _src and (chr(35)+' MULTI-NUM') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S124-S125-guards')
print('✅', done)

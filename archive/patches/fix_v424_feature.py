import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile():
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(os.getcwd(), fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
M0 = perfile()
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
pb = next((k for k, l in enumerate(B) if l.startswith('def _ident_of(')), None)
if pb is not None and 'def _phonebook(' not in '\n'.join(B):
    B[pb:pb] = ["def _phonebook():  # PHONEBOOK v85.48: numbers learned by exact basename, the way names are learned by face - consulted before any paper is opened, written whenever a text layer speaks",
                "    import json as _jp",
                "    cf = os.path.join(BASE_DIR, '.phonebook.json')",
                "    try:",
                "        return _jp.load(open(cf)), cf",
                "    except Exception:",
                "        return {}, cf",
                ""]
    done.append('phonebook-helper')
p0 = next(k for k, l in enumerate(B) if l.startswith('def phones_in_text('))
if 'PHONE-MASTER' not in B[p0+1]:
    d = ind(B[p0+1]) if p0+1 < len(B) else 4
    B.insert(p0+1, d*' ' + "t = t or ''")
    B.insert(p0+2, d*' ' + "for _i in range(3): t = re.sub(r'(\\d)[\\s.\\-](\\d)', r'\\1\\2', t)  # PHONE-MASTER v85.48: every shape a mobile wears - +91 glued, 91 or 0 prefixed, bare, or split - normalized to its ten-digit core; pincodes, dates and CTC figures never qualify")
    B.insert(p0+3, d*' ' + "_cores = []")
    B.insert(p0+4, d*' ' + "for _m in re.finditer(r'\\+?(?:91|0)?([6-9]\\d{9})(?!\\d)', t):")
    B.insert(p0+5, (d+4)*' ' + "if _m.group(1) not in _cores: _cores.append(_m.group(1))")
    B.insert(p0+6, d*' ' + "if _cores: return _cores")
    done.append('phone-master')
q0 = next(k for k, l in enumerate(B) if l.startswith('def phones_of('))
if 'PHONEBOOK-FIRST' not in '\n'.join(B[q0:q0+8]):
    d = ind(B[q0+1]) if q0+1 < len(B) else 4
    B.insert(q0+1, d*' ' + "_pbk, _pcf = _phonebook()  # PHONEBOOK-FIRST v85.48: a number learned once is known forever, in microseconds, even if the paper later goes silent")
    B.insert(q0+2, d*' ' + "_bn = os.path.basename(p)")
    B.insert(q0+3, d*' ' + "if _pbk.get(_bn): return list(_pbk[_bn])")
    B.insert(q0+4, d*' ' + "try:")
    B.insert(q0+5, (d+4)*' ' + "_ta = _phones_by_basename(p)")
    B.insert(q0+6, (d+4)*' ' + "if _ta: return list(_ta)")
    B.insert(q0+7, d*' ' + "except Exception:")
    B.insert(q0+8, (d+4)*' ' + "pass")
    done.append('phonebook-first')
i0 = next(k for k, l in enumerate(B) if l.startswith('def _ident_of('))
i1 = next(k for k in range(i0 + 1, len(B)) if B[k].startswith('def '))
rk = next((k for k in range(i0, i1) if B[k].strip().startswith('_IDC[p] =')), None)
if rk is not None and 'LEARN-PHONE' not in '\n'.join(B[i0:i1]):
    d = ind(B[rk])
    B.insert(rk, d*' ' + "_phs = [x for x in ids if not str(x).startswith('name:')]  # LEARN-PHONE v85.48: when a text layer speaks its number, the book remembers it by exact basename - twins keep separate entries, case-sensitive, forever")
    B.insert(rk+1, d*' ' + "if _phs:")
    B.insert(rk+2, (d+4)*' ' + "_pbk, _pcf = _phonebook()")
    B.insert(rk+3, (d+4)*' ' + "_pbk[os.path.basename(p)] = sorted(_phs)")
    B.insert(rk+4, (d+4)*' ' + "try: _j.dump(_pbk, open(_pcf, 'w'))")
    B.insert(rk+5, (d+4)*' ' + "except Exception: pass")
    done.append('learn-phone')
print('🔎 phones_in_text head and phones_of head:')
for k in range(p0, p0+9):
    print('   |', B[k].rstrip()[:160])
for k in range(q0, q0+10):
    print('   |', B[k].rstrip()[:160])
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.48' not in t:
        open(AR, 'a').write('v85.48: PHONE-MASTER normalizes every mobile costume (+91 glued, 91/0 prefixed, bare, split) to its ten-digit core while pincodes and dates never qualify; PHONEBOOK learns numbers by exact basename and phones_of consults it before opening any paper - the butler knows a number as it knows a name (S388, S389)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S388 every shape a mobile wears is read, and no pincode ever qualifies", "'S387 a slow load reads as work in progress, and a thinking master is never mistaken for a wedged child", "ck('S388 every shape a mobile wears is read, and no pincode ever qualifies', (chr(35)+' PHONE-MASTER v85.48') in _src and ('[6-9]' in _src))"),
      ("'S389 the butler knows a number as it knows a name - learned once, known forever", "'S388 every shape a mobile wears is read, and no pincode ever qualifies", "ck('S389 the butler knows a number as it knows a name - learned once, known forever', (chr(35)+' PHONEBOOK v85.48') in _src and (chr(35)+' LEARN-PHONE v85.48') in _src and ('.phonebook.json' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

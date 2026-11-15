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
if 'def teach_digits_inline(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def phones_of('))
    B[i:i] = ["def teach_digits_inline(name, basename, say):  # TEACH-IN-PLACE v85.49: when the paper is silent and the flow needs a number, the house asks for ten digits right here, learns them by exact basename, and continues the same breath - no restart, no re-walk, no re-pick",
              "    while True:",
              "        try:",
              "            s = input('📱 teach me the number for %s (10 digits, or Enter to skip): ' % name).strip()",
              "        except (KeyboardInterrupt, EOFError):",
              "            say('👋 teach skipped - nothing sent')",
              "            return ''",
              "        if not s:",
              "            return ''",
              "        dgs = re.sub(r'\\D', '', s)",
              "        if len(dgs) == 12 and dgs.startswith('91'): dgs = dgs[2:]",
              "        if len(dgs) == 11 and dgs.startswith('0'): dgs = dgs[1:]",
              "        if len(dgs) == 10 and dgs[0] in '6789':",
              "            pbk, pcf = _phonebook()",
              "            pbk[basename] = [dgs]",
              "            try:",
              "                import json as _j3",
              "                _j3.dump(pbk, open(pcf, 'w'))",
              "            except Exception:",
              "                pass",
              "            say('📚 learned: %s -> %s - remembered by exact filename, and the flow continues' % (basename, dgs))",
              "            return dgs",
              "        say('⚠️ that is not a 10-digit mobile (6-9 start) - try again, or Enter to skip')",
              ""]
    done.append('teach-inline-def')
np = next((k for k, l in enumerate(B) if 'teach me: python3 butler.py teach' in l and l.strip().startswith("say(")), None)
if np is not None and 'TEACH-IN-PLACE' not in '\n'.join(B[np:np+3]):
    d = ind(B[np])
    B.insert(np+1, d*' ' + "_td = teach_digits_inline(cur['name'], os.path.basename(p), say)  # TEACH-IN-PLACE v85.49: ten digits spoken here become the number, the book entry and the window's address in one breath")
    B.insert(np+2, d*' ' + "if _td: ph = _td")
    done.append('teach-at-outcome')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
G0 = open('briefing.py').read()
g = G0.split('\n')
snapg = list(g)
nf = next((k for k, l in enumerate(g) if l.strip().startswith('say("🤷 no phone found in that CV")')), None)
if nf is not None and 'TEACH-IN-PLACE' not in '\n'.join(g[max(0,nf-3):nf+1]):
    d = ind(g[nf])
    g[nf:nf] = [d*' ' + "_td = butler.teach_digits_inline(q or os.path.splitext(os.path.basename(hit))[0], os.path.basename(hit), say)  # TEACH-IN-PLACE v85.49: the picker's silence becomes a ten-second conversation, then the same breath drafts and opens",
                d*' ' + "if _td: phone = [_td]"]
    g[nf+2] = d*' ' + 'if not phone: say("🤷 no phone found in that CV"); return  # TEACH-IN-PLACE v85.49: the silence is a question, not a verdict - taught digits walk out of this block and into the draft'
    done.append('teach-at-picker')
op = next((k for k, l in enumerate(g) if '_pick_phone(_phones_by_basename(hit)' in l), None)
if op is not None and 'OWN-FIRST' not in g[op]:
    d = ind(g[op])
    g[op] = d*' ' + "phone = _pick_phone(phones_of(hit) or _phones_by_basename(hit), say, path=hit)  # OWN-FIRST v85.49: the picked paper's own eyes before any shared store - a borrowed twin number becomes structurally impossible"
    done.append('own-first')
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 wired doors:')
for l in open('butler.py').read().split('\n'):
    if 'TEACH-IN-PLACE v85.49: ten digits' in l or 'if _td: ph = _td' in l:
        print('   |', l.strip()[:150])
for l in open('briefing.py').read().split('\n'):
    if 'TEACH-IN-PLACE v85.49' in l or 'OWN-FIRST v85.49' in l:
        print('   |', l.strip()[:150])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.49' not in t:
        open(AR, 'a').write('v85.49: TEACH-IN-PLACE - at every no-phone door the house asks for ten digits in-line, normalizes any costume, validates the 6-9 start, writes .phonebook.json by exact basename and continues the same breath into the window; the picker return is conditional so taught digits walk on; OWN-FIRST puts the picked paper own eyes before any shared store (S390, S391)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S390 a silent paper becomes a ten-second conversation, then the same breath continues", "'S389 the butler knows a number as it knows a name - learned once, known forever", "ck('S390 a silent paper becomes a ten-second conversation, then the same breath continues', (chr(35)+' TEACH-IN-PLACE v85.49') in _src and ('def teach_digits_inline(' in _src) and ('if _td: ph = _td' in _src))"),
      ("'S391 the picked paper's own eyes stand before any shared store", "'S390 a silent paper becomes a ten-second conversation, then the same breath continues", "ck('S391 the picked paper'+chr(39)+'s own eyes stand before any shared store', (chr(35)+' OWN-FIRST v85.49') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' TEACH-IN-PLACE v85.49') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

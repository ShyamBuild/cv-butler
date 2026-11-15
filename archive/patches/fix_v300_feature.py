import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _chair_wa_text(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _chair_draft('))
    B[i:i] = ["CHAIR_SCENARIO = {'jd': 'jd', 'refer': 'refer', 'cv': 'nudge', 'missed': 'missed'}  # ONE-VOICE v84.19: the chair's outcomes map onto the keywords' scenarios",
              "def _chair_wa_text(kind, p, name):  # ONE-VOICE v84.19: the chair drafts through the same composer the keywords have always used; drafts/ and built-ins are fallbacks, not rivals",
              "    try:",
              "        import briefing as _br",
              "        sc = CHAIR_SCENARIO.get(kind)",
              "        if sc and hasattr(_br, '_fmt_tpl') and hasattr(_br, '_tpl_for'):",
              "            t = _br._fmt_tpl(_br._tpl_for([sc]), p, None, name)",
              "            if t and str(t).strip(): return str(t)",
              "    except Exception:",
              "        pass",
              "    return _chair_draft(kind, name, _pos_of(p, _pl_root()), p)",
              ""]
    done.append('one-voice')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if 'wa.send_review(ph, _chair_draft(draft, cur[' in l:
        B[k] = ind(l)*' ' + "wa.send_review(ph, _chair_wa_text(draft, p, cur['name']), say)"
        done.append('outcome-one-voice'); break
src = '\n'.join(B)
h0 = next(k for k, l in enumerate(B) if l.startswith('def _chase_draft('))
h1 = next(k for k in range(h0 + 1, len(B)) if B[k].startswith('def '))
if 'ONE-VOICE' not in '\n'.join(B[h0:h1]):
    B[h0:h1] = ["def _chase_draft(p, tag):  # CHASE v84.0 (v84.19): the background chase speaks through the same composer too",
                "    name = os.path.splitext(os.path.basename(p))[0]",
                "    sc = 'awaiting' if tag == 'Awaiting JD Confirmation' else 'nudge'",
                "    try:",
                "        import briefing as _br",
                "        t = _br._fmt_tpl(_br._tpl_for([sc]), p, None, name)",
                "        if t and str(t).strip(): return str(t)",
                "    except Exception:",
                "        pass",
                "    kind = 'jd' if tag == 'Awaiting JD Confirmation' else 'cv'",
                "    return _chair_draft(kind, name, _pos_of(p, _pl_root()), p)",
                ""]
    done.append('chase-one-voice')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S273 the chair drafts through the keywords' composer, not a rival clerk", "'S272 the roleline omits what was never taught", "ck('S273 the chair drafts through the keywords'+chr(39)+' composer, not a rival clerk', (chr(35)+' ONE-VOICE v84.19') in _src and ('def _chair_wa_text(' in _src) and ('_fmt_tpl' in _src))"),
      ("'S274 the fallback chain keeps every scenario speakable", "'S273 the chair drafts through the keywords' composer, not a rival clerk", "ck('S274 the fallback chain keeps every scenario speakable', ('def _chair_wa_text(' in _src) and ('def _draft_text(' in _src) and ('def _chair_draft(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

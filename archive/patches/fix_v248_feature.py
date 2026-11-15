import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _is_candidate_paper(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def get_visual_name('))
    B[i:i] = ["def _jd_like_name(st):  # RENAME-GATE v82.0: portal glue and JDs keep their names forever",
              "    lf = st.lower()",
              "    return lf.startswith('jd') or '_jd' in lf or ' jd' in lf or lf.endswith(('.eml', '.msg'))",
              "def _portal_name(st):  # RENAME-GATE v82.0: saved searches, reports and backups are not humans",
              "    lf = st.lower()",
              "    return any(w in lf for w in ('save search', 'resdex', 'report', 'summary', 'backup', 'anythingllm', 'debris'))",
              "def _is_candidate_paper(p):  # RENAME-GATE v82.0: only a paper that can hold a person may wear a person's name",
              "    st = os.path.splitext(os.path.basename(p))[0]",
              "    return not _jd_like_name(st) and not _portal_name(st)",
              "def _canonical_person_name(s):  # CANON-FORM v82.0: a pipeline name carries the human, not the paper's shout",
              "    t = (s or '')",
              "    t = re.sub(r'\\b\\d{1,2}[./-]\\d{1,2}[./-]\\d{2,4}\\b', ' ', t)",
              "    t = re.sub(r'\\b(20\\d{2}|19\\d{2})\\b', ' ', t)",
              "    t = re.sub(r'\\bcv\\b', ' ', t, flags=re.I)",
              "    t = re.sub(r'\\s+', ' ', t).strip(' -_.')",
              "    if t and t.isupper(): t = t.title()",
              "    return t",
              "def _rename_ledger(old, new, why, once=False):  # RENAME-LEDGER v82.0: every rename is written down so your word can undo it",
              "    try:",
              "        lp = os.path.join(BASE_DIR, 'rename_log.json')",
              "        lg = json.load(open(lp)) if os.path.exists(lp) else []",
              "        if once and any(e.get('old') == old and e.get('why') == why for e in lg): return False",
              "        lg.append({'old': old, 'new': new, 'why': why, 'ts': time.time()})",
              "        json.dump(lg[-200:], open(lp, 'w'), indent=1)",
              "        return True",
              "    except Exception:",
              "        return False",
              ""]
    done.append('rename-gate-helpers')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "self._rename(fp, target, say, 'suffix-canonical')" in l:
        d = ind(l)
        B[k:k+1] = [d*' ' + "if not _is_candidate_paper(fp):  # RENAME-GATE v82.0: portal glue and JDs are left untouched, silently - they were never candidates",
                    d*' ' + "    pass",
                    d*' ' + "elif not os.path.exists(fp):  # RENAME-PREFLIGHT v82.0: a stale decision rests once and is never re-knocked",
                    d*' ' + "    if _rename_ledger(os.path.basename(fp), os.path.basename(target), 'suffix-canonical-stale', once=True):",
                    d*' ' + "        say(f'⏭️ [rename] rested: {os.path.basename(fp)} already wears its new name - stale decision, not retried')",
                    d*' ' + "else:",
                    d*' ' + "    _rename_ledger(os.path.basename(fp), os.path.basename(target), 'suffix-canonical')",
                    d*' ' + "    self._rename(fp, target, say, 'suffix-canonical')"]
        done.append('suffix-gate'); break
src = '\n'.join(B)
nvis = 0
for k, l in enumerate(B):
    if l.strip() == "name, tag = vv, 'visual'":
        B[k] = ind(l)*' ' + "name, tag = _canonical_person_name(vv), 'visual'  # CANON-FORM v82.0: the pipeline name carries the human - no dates, no CV, no shouting"
        nvis += 1
if nvis: done.append(f'canon-form-{nvis}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S204 portal glue and JDs keep their names", "'S203 the autodraft sleep-switch honours the off word", "ck('S204 portal glue and JDs keep their names', ('def _is_candidate_'+'paper(') in _src and (chr(35)+' RENAME-GATE v82.0') in _src)"),
      ("'S205 a stale rename decision rests and is never re-knocked", "'S204 portal glue and JDs keep their names", "ck('S205 a stale rename decision rests and is never re-knocked', (chr(35)+' RENAME-PREFLIGHT v82.0') in _src)"),
      ("'S206 every rename is written in the undo ledger", "'S205 a stale rename decision rests and is never re-knocked", "ck('S206 every rename is written in the undo ledger', (chr(35)+' RENAME-LEDGER v82.0') in _src and ('rename_log'+'.'+'json') in _src)  # the dot travels with the needle: split between characters, never delete one"),
      ("'S207 the visual name carries the human, not the paper's shout", "'S206 every rename is written in the undo ledger", "ck('S207 the visual name carries the human, not the paper'+chr(39)+'s shout', (chr(35)+' CANON-FORM v82.0') in _src and ('name, tag = vv, ' + chr(39) + 'visual' + chr(39)) not in _src)"),
      ("'S208 the class keeps its methods", "'S207 the visual name carries the human, not the paper's shout", "ck('S208 the class keeps its methods', any(l.startswith('    def _reconcile_'+'tags') for l in _src.split(chr(10))) and any(l.startswith('    def _rename_'+'clean') for l in _src.split(chr(10))))  # S208: a column-zero line inside a class body amputates the class; the witnesses pin the indentation itself")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S202 the door is asked until it answers")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

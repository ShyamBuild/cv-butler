import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# PIPELINE-CLI-FIRST v83.1' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if not os.path.isdir(root):')
    d = ind(B[i])
    B[i:i] = [d*' ' + "if len(sys.argv) > 1 and sys.argv[1] in ('pending', 'status', 'note'):  # PIPELINE-CLI-FIRST v83.1: a question is never a folder - the verbs answer before any root is validated",
              d*' ' + "    _v, _a = sys.argv[1], sys.argv[2:]",
              d*' ' + "    if _v == 'pending': pipeline_pending(_a[0] if _a else None, print)",
              d*' ' + "    elif _v == 'status': pipeline_status(' '.join(_a), print)",
              d*' ' + "    else: pipeline_note(_a[0] if _a else '', ' '.join(_a[1:]), print)",
              d*' ' + "    sys.exit(0)"]
    done.append('cli-first')
    src = '\n'.join(B)
i0 = next(k for k, l in enumerate(B) if l.startswith('def _pl_root():'))
i1 = next(k for k, l in enumerate(B) if l.startswith('def _tags_of('))
if 'os.kill(pid, 0)' not in '\n'.join(B[i0:i1]):
    B[i0:i1] = ["def _pl_root():  # PIPELINE v83.0 (hardened v83.1): a lock must prove its holder lives and its world exists before it may name the world",
                "    cands = []",
                "    try:",
                "        for f in os.listdir(BASE_DIR):",
                "            if f.startswith('butler_') and f.endswith('.lock'):",
                "                try:",
                "                    pid_s, rt = open(os.path.join(BASE_DIR, f)).read().split('|', 1)",
                "                    pid = int(pid_s.strip()); rt = rt.strip()",
                "                    os.kill(pid, 0)",
                "                    if rt.startswith('/') and os.path.isdir(rt): cands.append(rt)",
                "                except Exception:",
                "                    continue",
                "    except Exception:",
                "        pass",
                "    if cands: return cands[0]",
                "    return os.path.join(os.path.expanduser('~'), 'Downloads', 'Sunsoft Technology')"]
    done.append('pl-root-hardened')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
g = [l for l in g if not (l.strip().startswith("if q.startswith('pending'): do_pending(") or l.strip().startswith("if q.startswith('status'): do_status(") or l.strip().startswith("if q.startswith('note'): do_note("))]
srcg = '\n'.join(g)
if '# PIPELINE-CHAT-SHALLOW v83.1' not in srcg:
    g = srcg.split('\n')
    i = next(k for k, l in enumerate(g) if l.strip() == "if q.lower().startswith('focus'):")
    d = ind(g[i])
    g[i:i] = [d*' ' + "if q.startswith('pending'): do_pending(q[len('pending'):].strip(), root); continue  # PIPELINE-CHAT-SHALLOW v83.1: the master's words stand at the head of the chain, never nested under another voice",
              d*' ' + "if q.startswith('status'): do_status(q[len('status'):].strip(), root); continue",
              d*' ' + "if q.startswith('note'): do_note(q[len('note'):].strip(), root); continue"]
    done.append('chat-shallow')
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S214 a question is never a folder", "'S213 terminal tags never clock", "ck('S214 a question is never a folder', 0 <= _src.find(\"sys.argv[1] in ('pend\"+\"ing', 'status', 'note')\") < _src.find('if not os.path.isdir('+'root):'))"),
      ("'S215 a lock must prove its holder lives before it names the world", "'S214 a question is never a folder", "ck('S215 a lock must prove its holder lives before it names the world', 'os.kill(' in _src[_src.find('def _pl_root():'):_src.find('def _tags_of(')])"),
      ("'S216 the master's words stand at the head of the chat chain", "'S215 a lock must prove its holder lives before it names the world", "ck('S216 the master'+chr(39)+'s words stand at the head of the chat chain', ((_b := open(os.path.join(BASE_DIR, 'briefing.py')).read()) and _b.count(\"if q.startswith('pending'): do_pending(\") == 1 and _b.find(\"if q.startswith('pending'): do_pending(\") < _b.find(\"if q.lower().startswith('missed'):\")))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S212 the overdue nudge rests like every machine-born voice")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
_b = open('briefing.py').read()
print('DIAG cli_first_before_isdir:', 0 <= src.find("sys.argv[1] in ('pending'") < src.find('if not os.path.isdir(root):'))
print('DIAG pl_root_proves_life:', 'os.kill(' in src[src.find('def _pl_root():'):src.find('def _tags_of(')])
print('DIAG chat_shallow:', _b.find("if q.startswith('pending'): do_pending(") < _b.find("if q.lower().startswith('missed'):"))
print('✅', done)

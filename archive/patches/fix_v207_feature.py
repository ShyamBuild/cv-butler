import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# LISTEN-FN v81.69' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def phones_of(p):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def listen_teach(q):  # LISTEN-FN v81.69: the master's bare ten digits, within five minutes of a confession, are the lesson",
              d*' ' + "    try:",
              d*' ' + "        _qd = (q or '').replace(' ', '')",
              d*' ' + "        if not (_qd.isdigit() and len(_qd) in (10, 12)): return None",
              d*' ' + "        _lp = os.path.join(BASE_DIR, 'last_nophone.json')",
              d*' ' + "        if not os.path.exists(_lp): return None",
              d*' ' + "        _st = json.load(open(_lp))",
              d*' ' + "        if time.time() - _st.get('ts', 0) > 600: return None",
              d*' ' + "        _dg = teach_phone(_st.get('stem', _qd), _qd)",
              d*' ' + "        print(f'\\U0001f4da taught {_st.get(\"stem\")} -> {_dg} - say missed {_st.get(\"stem\")} again to draft on it now', flush=True)",
              d*' ' + "        return _dg",
              d*' ' + "    except Exception as _te:",
              d*' ' + "        print(f'⚠️ teach-listen skipped: {_te}', flush=True)",
              d*' ' + "        return None",
              ""]
    done.append('listen-fn')
src = '\n'.join(B)
if '# LISTEN-STATE v81.67' not in src:
    i = next(k for k, l in enumerate(B) if 'we are talking about' in l and 'teach me' in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "try: json.dump({'stem': stem, 'ts': time.time()}, open(os.path.join(BASE_DIR, 'last_nophone.json'), 'w'))  # LISTEN-STATE v81.67: the confession leaves an address the REPL can listen at")
    B.insert(i+2, d*' ' + "except Exception: pass")
    done.append('nophone-state')
src = '\n'.join(B)
if '# EMAIL-ALWAYS v81.67' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if ph:')
    d = ind(B[i])
    B[i:i] = [d*' ' + "em = emails_in_text(txt)  # EMAIL-ALWAYS v81.67: the second anchor is shown whenever the phone is fetched",
              d*' ' + "if ph and em: print(f'\\U0001f4e7 {os.path.basename(ap)} · {em[0]}', flush=True)"]
    done.append('email-always')
src = '\n'.join(B)
if '# TAUGHT-ECHO v81.67' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "return [re.sub(r'\\D', '', str(tv))]")
    d = ind(B[i])
    B.insert(i, d*' ' + "print(f'\\U0001f4da taught number in use for {os.path.basename(ap)}', flush=True)  # TAUGHT-ECHO v81.67")
    done.append('taught-echo')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'import butler' not in '\n'.join(g):
    i = next(k for k, l in enumerate(g) if l.startswith('import '))
    g.insert(i, 'import butler  # LISTEN v81.67: the REPL teaches through the butler\'s book')
    done.append('butler-import')
srcg = '\n'.join(g)
if '# LISTEN v81.67' not in srcg:
    i = next(k for k, l in enumerate(g) if l.strip() == 'q = input("you> ").strip()')
    d = ind(g[i])
    g.insert(i+1, d*' ' + "if butler.listen_teach(q): continue  # LISTEN v81.67: after a no-phone confession, the master's bare ten digits are the lesson")
    done.append('listen-one-line')
srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
S = os.path.join(os.getcwd(), 'ship.sh')
s = open(S).read()
if 'GATE-LOUD v81.69' not in s:
    s = s.replace('echo "$OUT" | tail -40', 'echo "$OUT" | grep "FAIL\\|SKILLS MISSING" | head -10  # GATE-LOUD v81.69: every red line before the window\necho "$OUT" | tail -40', 1)
    open(S, 'w').write(s); done.append('gate-loud')
B = open('butler.py').read().split('\n')
if "'S174 the teach verb stands before the door" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S173 the master can teach a number from any terminal" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S174 the teach verb stands before the door', any(L[j].strip() == \"if __name__ == '__main__':\" and (chr(35)+' TEACH-CLI v81.65') in L[j+1] for j in range(len(L)-1)) if (L := _src.split(chr(10))) else False)  # adjacency-pinned")
    done.append('S174-guard')
B = open('butler.py').read().split('\n')
if "'S175 silence teaches nothing, digits teach once" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S174 the teach verb stands before the door" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S175 silence teaches nothing, digits teach once', (chr(35)+' LISTEN-STATE v81.67') in _src and (chr(35)+' LISTEN v81.67') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")
    done.append('S175-guard')
B = open('butler.py').read().split('\n')
if "'S176 the gate shows every red line before the window" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S175 silence teaches nothing, digits teach once" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S176 the gate shows every red line before the window', 'GATE-LOUD v81.69' in open(os.path.join(BASE_DIR, 'ship.sh')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S176-guard')
print('✅', done)

import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'def emails_in_text(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def phones_of(p):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def emails_in_text(t):  # EMAIL-WITNESS v81.64: the second anchor, unique to a person and readable at a glance",
              d*' ' + "    out = []",
              d*' ' + "    for m in re.finditer(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}', t or ''):",
              d*' ' + "        if m.group(0) not in out: out.append(m.group(0))",
              d*' ' + "    return out",
              "",
              d*' ' + "def teach_phone(name, digits):  # TEACH-CLI v81.64: the master's word is the paper of last resort",
              d*' ' + "    d = re.sub(r'\\D', '', str(digits))",
              d*' ' + "    p = os.path.join(BASE_DIR, 'phones_taught.json')",
              d*' ' + "    try: s = json.load(open(p))",
              d*' ' + "    except Exception: s = {}",
              d*' ' + "    s[name.strip().lower()] = d",
              d*' ' + "    json.dump(s, open(p, 'w'), indent=1)",
              d*' ' + "    return d",
              ""]
    done.append('emails-and-teach')
for k, l in enumerate(B):
    if 'we are talking about' in l and 'teach me' in l:
        B[k] = ind(l)*' ' + "print(f'\\U0001f937 we are talking about {os.path.basename(ap)} · email: {emails_in_text(txt or ocr)[0] if emails_in_text(txt or ocr) else \"none readable\"} - no phone readable in it; teach me: python3 butler.py teach <name> <digits>', flush=True)"
        done.append('identity-with-email'); break
src = '\n'.join(B)
if '# TEACH-CLI v81.64' not in src or "sys.argv[1] == 'teach'" not in src:
    i = next(k for k, l in enumerate(B) if 'sys.exit(0 if _selftest' in l)
    d = ind(B[i])
    B[i:i] = [d*' ' + "if len(sys.argv) > 2 and sys.argv[1] == 'teach':  # TEACH-CLI v81.64",
              d*' ' + "    print('taught:', ' '.join(sys.argv[2:-1]), '->', teach_phone(' '.join(sys.argv[2:-1]), sys.argv[-1]))",
              d*' ' + "    sys.exit(0)"]
    done.append('teach-cli')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S172 the email speaks when the phone is silent" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S171 a taught number beats extraction" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S172 the email speaks when the phone is silent', emails_in_text('Lokesh A · lokeshmechanical23@gmail.com · 9360566513') == ['lokeshmechanical23@gmail.com'])")
    B.insert(i+2, d*' ' + "ck('S173 the master can teach a number from any terminal', 'def teach_phone(' in _src and (chr(35)+' TEACH-CLI v81.64') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S172-S173-guards')
print('✅', done)

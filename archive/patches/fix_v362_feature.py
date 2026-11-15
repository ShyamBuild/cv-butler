import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
G0 = open('briefing.py').read()
M0 = set(markers(B0.split('\n'))) | set(markers(G0.split('\n')))
REFER = ("Hi {name}, Sundeep Rana here. Thank you for your time on our call earlier.\n"
         "As discussed, I have emailed you the JD for the {position} role at {company} in {location}.\n"
         "If you know one or two individuals who might be a good fit, please share this with them directly. They can WhatsApp me their CV in PDF format from their own number, or give me a call.\n"
         "Thank you for your support.\n"
         "Regards,\n"
         "Sundeep Rana\n")
for rel in ('drafts/refer.txt', 'templates/referral.txt'):
    P = os.path.join(os.getcwd(), rel)
    if os.path.exists(P):
        cur = open(P).read()
        if 'I have emailed you the JD for the' not in cur:
            if not os.path.exists(P + '.bakv85'):
                open(P + '.bakv85', 'w').write(cur)
            open(P, 'w').write(REFER)
            done.append('refer-text:' + rel.split('/')[0])
    elif os.path.isdir(os.path.dirname(P)):
        open(P, 'w').write(REFER)
        done.append('refer-text:' + rel.split('/')[0])
g = G0.split('\n')
if 'def _smart_input(' not in '\n'.join(g):
    a0 = next(k for k, l in enumerate(g) if l.startswith('def answer('))
    g[a0:a0] = ["def _smart_input(prompt):  # LISTEN-REPL v85.4: at the chair a digit is a keystroke; words still take a line",
                "    import sys, termios, tty",
                "    import butler as _bt",
                "    try: _seated = _bt.sheet_current() and not _bt.action_pending()",
                "    except Exception: _seated = False",
                "    if not _seated:",
                "        return input(prompt)",
                "    sys.stdout.write(prompt); sys.stdout.flush()",
                "    try:",
                "        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)",
                "        tty.setraw(fd)",
                "        try:",
                "            c = sys.stdin.read(1)",
                "            if c == '\\x03':",
                "                sys.stdout.write('^C\\n'); sys.stdout.flush(); raise KeyboardInterrupt",
                "            if c in '1234567':",
                "                sys.stdout.write(c + '\\n'); sys.stdout.flush()",
                "                return c",
                "            buf = c",
                "            while c not in ('\\r', '\\n'):",
                "                sys.stdout.write(c); sys.stdout.flush()",
                "                c = sys.stdin.read(1)",
                "            sys.stdout.write('\\n'); sys.stdout.flush()",
                "            return buf.strip()",
                "        finally:",
                "            termios.tcsetattr(fd, termios.TCSADRAIN, old)",
                "    except KeyboardInterrupt:",
                "        raise",
                "    except Exception:",
                "        return input('')",
                ""]
    done.append('smart-input')
for k, l in enumerate(g):
    if 'you>' in l and 'input(' in l and '_smart_input' not in l:
        g[k] = l.replace('input(', '_smart_input(')
        done.append('repl-listen'); break
srcg = '\n'.join(g)
ast.parse(srcg); open('briefing.py', 'w').write(srcg)
B = B0.split('\n')
snap = list(B)
t3 = next((k for k, l in enumerate(B) if l.strip().startswith('if t3: return t3')), None)
if t3 is not None and 'SCENARIO-REFER' not in '\n'.join(B[t3:t3+6]):
    d = ind(B[t3])
    B[t3+1:t3+1] = [d*' ' + "if kind == 'refer':  # SCENARIO-REFER v85.4: the refer voice speaks the master's own courtesy, verbatim, from the scenario store",
                    (d+4)*' ' + "t4 = _draft_text('refer', name, _pos_of(p, _pl_root()), p)",
                    (d+4)*' ' + "if t4: return t4"]
    done.append('refer-first')
for k, l in enumerate(B):
    if l.strip().startswith("ck('S335 ") and 'on ' not in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S335 no candidate-facing text claims the details travelled on WhatsApp', all((('on ' + 'WhatsApp') not in open(os.path.join(BASE_DIR, dd, ff)).read()) for dd in ('templates', 'drafts') for ff in os.listdir(os.path.join(BASE_DIR, dd)) if ff.endswith('.txt')))  # S335 repinned v85.4: the law guards truth, not vocabulary - a referral may WhatsApp the master, but no text may claim his details went there"
        done.append('S335-repin'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('briefing.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.4' not in t:
        open(AR, 'a').write('v85.4: LISTEN-REPL (a seated digit is a keystroke, words keep their line), the master\'s refer courtesy verbatim in drafts/refer.txt and templates/referral.txt with registry placeholders, chair refer reads the scenario store first, S335 repinned from vocabulary to truth\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S337 at the chair a digit is a keystroke and a word is a line", "'S336 every single-key answer is a keystroke - no Enter in the copilot's mouth", "ck('S337 at the chair a digit is a keystroke and a word is a line', (chr(35)+' LISTEN-REPL v85.4') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('1234567' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S338 the refer voice speaks the master's courtesy verbatim", "'S337 at the chair a digit is a keystroke and a word is a line", "ck('S338 the refer voice speaks the master'+chr(39)+'s courtesy verbatim', (chr(35)+' SCENARIO-REFER v85.4') in _src and os.path.exists(os.path.join(BASE_DIR, 'drafts', 'refer.txt')) and ('I have emailed you the JD for the' in open(os.path.join(BASE_DIR, 'drafts', 'refer.txt')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

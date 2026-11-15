import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
i0 = next((k for k, l in enumerate(B) if l.strip().startswith('def _ad_fire(self, d, txt, v, nm, say):')), None)
if i0 is not None and '# AD-FIRE v81.5' not in '\n'.join(B):
    i1 = next(k for k in range(i0+1, i0+20) if B[k].strip().startswith('def ') and ind(B[k]) == ind(B[i0]))
    d = ind(B[i0])
    B[i0:i1] = [d*' ' + "def _ad_fire(self, d, txt, v, nm, say):  # AD-FIRE v81.5 (subprocess: playwright needs a main thread)",
                d*' ' + "    import subprocess, sys",
                d*' ' + "    self._ad_pending = _t.time() + 75",
                d*' ' + "    say(f'📝 autodraft: {v} -> +{d} ({nm})')",
                d*' ' + "    try:",
                d*' ' + "        tf = os.path.join(BASE_DIR, 'ad_draft.txt')",
                d*' ' + "        open(tf, 'w').write(txt)",
                d*' ' + "        lf = open(os.path.join(BASE_DIR, 'ad_fire.log'), 'a')",
                d*' ' + "        subprocess.Popen([sys.executable, '-c', 'import wa, sys; wa.send_review(sys.argv[1], open(sys.argv[2]).read(), print)', d, tf], cwd=BASE_DIR, stdout=lf, stderr=subprocess.STDOUT)",
                d*' ' + "    except Exception as e:",
                d*' ' + "        say(f'⚠️ autodraft fire failed: {e}')",
                ""]
    done.append('ad-fire-subprocess')
src = '\n'.join(B)
old = "            if not os.path.exists(fp) or _settling(fp): say(f'⏭️ autodraft skip (moved or settling): {os.path.basename(fp)}'); return"
if old in src:
    i = next(k for k, l in enumerate(B) if l == old)
    d = ind(B[i])
    B[i:i+1] = [d*' ' + "if not os.path.exists(fp):",
                d*' ' + "    hit = None",
                d*' ' + "    for dp, dn, fn in os.walk(self.root):",
                d*' ' + "        dn[:] = [x for x in dn if not x.startswith('.')]",
                d*' ' + "        if os.path.basename(fp) in fn: hit = os.path.join(dp, os.path.basename(fp)); break",
                d*' ' + "    if not hit: say(f'⏭️ autodraft skip (gone): {os.path.basename(fp)}'); return",
                d*' ' + "    fp = hit",
                d*' ' + "if _settling(fp): say(f'⏭️ autodraft skip (settling): {os.path.basename(fp)}'); return"]
    done.append('draft-relocate')
src = '\n'.join(B)
if '# TAGADD-LOG v81.5' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if v: self._draft_one(fp, tg, v, mode, say)')
    d = ind(B[i])
    B.insert(i, d*' ' + "say(f'🏷️ tag-add: {os.path.basename(fp)} +{tg}')  # TAGADD-LOG v81.5")
    done.append('tagadd-log')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S112 drafts fire in their own process" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S111 pulse clock uses the file's own alias" in l or "'S111 pulse clock uses the file own alias" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S112 drafts fire in their own process', (chr(35)+' AD-FIRE v81.5') in _src and 'threading.Thread' not in _src.split('def _ad_fire')[1].split('def _draft_one')[0])")
    B.insert(i+2, d*' ' + "ck('S113 every tag-add is witnessed', (chr(35)+' TAGADD-LOG') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S112-S113-guards')
print('✅', done)

import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
out = []; skip = 0
for l in B:
    if skip > 0: skip -= 1; continue
    if "sys.argv[1] == 'teach'" in l and '# TEACH-CLI v81.64' in l:
        skip = 2; done.append('teach-cli-removed'); continue
    out.append(l)
B = out
src = '\n'.join(B)
if '# TEACH-CLI v81.65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "if __name__ == '__main__':")
    d = 4
    B[i+1:i+1] = [d*' ' + "if len(sys.argv) > 2 and sys.argv[1] == 'teach':  # TEACH-CLI v81.65: first word at the door, before any folder argument is imagined",
                  d*' ' + "    print('taught:', ' '.join(sys.argv[2:-1]), '->', teach_phone(' '.join(sys.argv[2:-1]), sys.argv[-1]), flush=True)",
                  d*' ' + "    sys.exit(0)"]
    done.append('teach-cli-at-door')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S174 the teach verb stands before the door" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S173 the master can teach a number from any terminal" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S174 the teach verb stands before the door', (chr(35)+' TEACH-CLI v81.65') in _src and _src.find(chr(35)+' TEACH-CLI v81.65') < _src.find('    main()'))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S174-guard')
print('✅', done)

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
    B[i+1:i+1] = ["    if len(sys.argv) > 2 and sys.argv[1] == 'teach':  # TEACH-CLI v81.65: first word at the door, before any folder argument is imagined",
                  "        print('taught:', ' '.join(sys.argv[2:-1]), '->', teach_phone(' '.join(sys.argv[2:-1]), sys.argv[-1]), flush=True)",
                  "        sys.exit(0)"]
    done.append('teach-cli-at-door')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if "'S174 the teach verb stands before the door" in l:
        B[k] = ind(l)*' ' + "ck('S174 the teach verb stands before the door', any(L[j].strip() == \"if __name__ == '__main__':\" and (chr(35)+' TEACH-CLI v81.65') in L[j+1] for j in range(len(L)-1)) if (L := _src.split(chr(10))) else False)  # adjacency-pinned: a witness cannot trip on its own quotation"
        done.append('S174-repinned'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

import ast, os, shutil
p = 'butler.py'; L = open(p).read().split('\n'); done = []
print('selftest defs:', sum(1 for l in L if l.strip().startswith('def _selftest(')))
print('main guard present:', any(l.strip().startswith("if __name__ == '__main__':") for l in L))
if not any(l.strip().startswith("if __name__ == '__main__':") for l in L):
    while L and not L[-1].strip():
        L.pop()
    L += ['',
          "if __name__ == '__main__':",
          "    if len(sys.argv) > 2 and sys.argv[1] == '--selftest':",
          "        sys.exit(0 if _selftest(sys.argv[2]) else 1)",
          "    main()"]
    done.append('module-tail-restored')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
shutil.copy(p, os.path.expanduser('~/pending_v30/butler.py'))
print('✅', done or 'nothing missing')

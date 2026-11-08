#!/usr/bin/env python3
import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_here))
sys.path.insert(0, os.path.expanduser('~/CV_Tool'))
try:
    import butler
except Exception as _e:
    print('rendiag cannot import butler; sys.path was:')
    for p in sys.path:
        print('  ', p)
    raise
deep = '--deep' in sys.argv[1:]
args = [a for a in sys.argv[1:] if a != '--deep']
paths = []
for a in args:  # RENDIAG-FOLDERS v85.85: a folder argument walks every subfolder of any chair, so other desks diagnose in one command
    if os.path.isdir(a):
        for dp, dn, fn in os.walk(a):
            for x in fn:
                if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):
                    paths.append(os.path.join(dp, x))
            if len(paths) > 400: break
    else:
        paths.append(a)
if not paths:
    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()
    for dp, dn, fn in os.walk(root):
        for x in fn:
            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):
                paths.append(os.path.join(dp, x))
        if len(paths) > 400: break
try:
    butler.rename_diag(paths, deep=deep)
except BrokenPipeError:  # PIPE-GRACE v85.86: when the reader stops listening (head, less, a closed window), the table dies quietly instead of tracebacking over its own rows
    os._exit(0)

import os, shutil, sys
import butler, briefing
ROOT = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
ok = True
def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('PASS' if cond else 'FAIL'), name, extra)
B = butler.Butler(ROOT)
check('S1 class bindings', all(hasattr(butler.Butler, m) for m in ('route','_route','handle_tags','_reconcile_tags','handle_pdf','normalize_suffix','_archive_source')))
pr = os.path.join(ROOT, 'Call Scheduled', 'Pradip Amte.pdf')
tg = butler.get_tags(pr) if os.path.exists(pr) else []
check('S2 tag reading', any('Closed' in t for t in tg), str(tg))
B._reconcile_tags(print)
pr2 = os.path.join(ROOT, 'Closed – Not Proceeding', 'Pradip Amte.pdf')
check('S3 tag-driven move (Pradip)', os.path.exists(pr2))
src = os.path.join(ROOT, 'Mohit Mathur.pdf'); tmp = os.path.join(ROOT, 'zz_garbage_test.pdf')
if os.path.exists(src):
    shutil.copy(src, tmp)
    B.route(tmp, print)
    renamed = not os.path.exists(tmp)
    check('S4 wrong-name repair', renamed)
    for f in os.listdir(ROOT):
        if f.startswith('zz_garbage_test') or f.startswith('Mohit Mathur_'):
            os.remove(os.path.join(ROOT, f))
data = briefing.collect(ROOT)
check('S5 board shows closed row', len(data.get('closed - not proceeding', [])) >= 1)
print('ALL GREEN' if ok else 'SKILLS MISSING - see FAILs above')
sys.exit(0 if ok else 1)

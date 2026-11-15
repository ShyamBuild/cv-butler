import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import butler
for p in sys.argv[1:]:
    if not os.path.exists(p):
        print('== %s   (not on disk under that name - healed or renamed)' % os.path.basename(p)); continue
    print('== %s' % os.path.basename(p))
    a = ''
    try:
        import pypdf
        a = '\n'.join((pg.extract_text() or '') for pg in pypdf.PdfReader(p).pages)
        print('   pypdf  : %4d chars | %s' % (len(a), (a or '')[:60].replace(chr(10), ' | ')))
    except Exception as e:
        print('   pypdf  : ERR %s' % repr(e)[:60])
    try:
        b = butler._pdf_pure_text(p) or ''
        print('   pure   : %4d chars | %s' % (len(b), b[:60].replace(chr(10), ' | ')))
    except Exception as e:
        print('   pure   : ERR %s' % repr(e)[:60])
    c = ''
    try:
        c = butler.extract_text_ocr(p) or ''
        print('   vision : %4d chars | %s' % (len(c), (c or '')[:60].replace(chr(10), ' | ')))
    except Exception as e:
        print('   vision : ERR %s' % repr(e)[:60])
    t = a if len(a) >= len(c) else c
    print('   brain  : %s' % (butler._eyename_of(p) or 'SILENT'))
    print('   emails : %s' % (butler.emails_in_text(t)[:2] or ['none']))
    print('   phones : %s' % (butler.phones_in_text(t)[:3] or ['none']))
    print('   on disk: %s' % os.path.basename(p))

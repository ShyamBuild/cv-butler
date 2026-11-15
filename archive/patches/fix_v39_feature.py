P = open('PROTOCOL.md').read()
if 'Patch scripts are authored' not in P:
    P = P.rstrip() + '\n15. Patch scripts are authored directly into ~/CV_Tool/archive/patches/ (never the home folder); each is a one-shot delivery envelope, inert after ship.sh runs it once.\n'
    open('PROTOCOL.md', 'w').write(P)
    print('✅ PROTOCOL rule 15 added')
else:
    print('✅ rule already present')

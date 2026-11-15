s = open('ship.sh').read()
s2 = s.replace('echo "$OUT" | tail -20', 'echo "$OUT" | tail -40')
if s2 != s:
    open('ship.sh', 'w').write(s2)
    print('✅ gate now shows the full skill list (tail -40)')
else:
    print('✅ already showing full list')

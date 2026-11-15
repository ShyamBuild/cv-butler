import ast, os
done = []
F = open('briefing.py').read()
old_syn = "    SYN = {'nudge': 'awaiting', 'reminder': 'awaiting', 'followup': 'outbox', 'follow': 'outbox', 'chase': 'outbox', 'refer': 'reference', 'referral': 'reference', 'goodluck': 'interview', 'wish': 'interview', 'fb': 'feedback'}"
new_syn = "    SYN = {'nudge': 'awaiting', 'reminder': 'awaiting', 'followup': 'outbox', 'follow': 'outbox', 'chase': 'outbox', 'goodluck': 'interview', 'wish': 'interview', 'fb': 'feedback'}"
if old_syn in F:
    F = F.replace(old_syn, new_syn, 1); done.append('syn-unshadow-referral')
open('briefing.py', 'w').write(F); ast.parse(F)
B = open('butler.py').read().split('\n')
if "'S64 referral voice not shadowed" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S63 referral voice for closed candidates" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "ck('S64 referral voice not shadowed', \"'referral': 'reference'\" not in _br and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'referral.txt')))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S64-guard')
print('✅', done)

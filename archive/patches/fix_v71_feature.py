import ast, os
done = []
T = {
'missed.txt': "Hi {name}, Sundeep Rana (Sunsoft Technology) - tried calling you today.\nRegarding the {position} role | {where_line}.\nPlease share your updated CV (PDF) here + a good time to reconnect. Thanks!",
'jd.txt': "Hi {name}, sharing the JD for the {position} role | {where_line}.\nKindly confirm receipt and share your interest, current CTC & notice period.\nLooking forward to your reply. Thanks!",
'awaiting.txt': "Hi {name}, a gentle reminder on the {position} role I shared.\nA one-line reply (interested / not now) helps me close the loop.\nThank you!",
'touch.txt': "Hi {name}, hope you're doing well.\nKeeping you in mind for roles like {position} | {where_line}.\nAny update on your search or CV? A line back would be great.",
'rejected.txt': "Hi {name}, thank you for your time on the {position} role.\nThe client is moving ahead with other profiles - not a reflection on you.\nI'd love to stay in touch for future matches. All the best!",
'reference.txt': "Hi {name}, thanks for the honest reply earlier.\nAs discussed, here are the {position} details | {where_line}.\nWhenever convenient, please share 1-2 referrals who may fit - I'd be grateful.",
'outbox.txt': "Hi {name}, following up on my last message about the {position} role.\nA quick update from you helps me proceed or close the loop.\nThanks!",
'interview.txt': "Hi {name}, best wishes for your {position} interview!\nReach 10 minutes early with a CV copy; message me once you're done.\nI'm right here if you need anything at all.",
'feedback.txt': "Hi {name}, hope the {position} interview went well.\nCould you share how it went and any feedback you received?\nI'll follow up with the client today and keep you posted.",
}
os.makedirs('templates', exist_ok=True)
for f, body in T.items():
    open(os.path.join('templates', f), 'w').write(body + '\n')
open('wa_template.txt', 'w').write(T['missed.txt'] + '\n')
done.append(f'templates-x{len(T)}+default')
F = open('briefing.py').read()
if 'reconnect. Thanks!")' not in F:
    i = F.index('DEFAULT_TPL = (')
    j = F.index('Sunsoft Technology")', i) + len('Sunsoft Technology")')
    F = F[:i] + ('DEFAULT_TPL = ("Hi {name}, Sundeep Rana (Sunsoft Technology) - tried calling you today.\\n"\n'
                 '"Regarding the {position} role | {where_line}.\\n"\n'
                 '"Please share your updated CV (PDF) here + a good time to reconnect. Thanks!")') + F[j:]
    open('briefing.py', 'w').write(F); ast.parse(F); done.append('default-tpl-short')
C = open('cadence.py').read()
old = "            want = 'reference' if i['kind'] == 'reference_ask' else 'outbox'"
if old in C:
    C = C.replace(old, "            KIND_TPL = {'reference_ask': 'reference', 'interview_eve': 'interview', 'interview_morning': 'interview', 'interview_feedback_ask': 'feedback', 'interview_nextday_chase': 'feedback'}\n            want = KIND_TPL.get(i['kind'], 'outbox')", 1)
    done.append('kind-aware-templates')
oldf = "            text = base.format(name=(nm.title() or 'there'), position=f.get('display', 'your application'), company=f.get('client', 'Sunsoft Technology'))"
if oldf in C:
    C = C.replace(oldf, "            text = briefing._fmt_tpl(base, (briefing._hits_for(nm, root) or [None])[0], f, (nm.title() or 'there'))", 1)
    done.append('outbox-uses-fmt-tpl')
open('cadence.py', 'w').write(C); ast.parse(C)
B = open('butler.py').read().split('\n')
if "'S55 scenario templates" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S54 position/location split wired" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "_td = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')")
    B.insert(i+2, d*' ' + "ck('S55 scenario templates + kind-aware outbox', os.path.isdir(_td) and len([f for f in os.listdir(_td) if f.endswith('.txt')]) >= 9 and '_fmt_tpl(base,' in _cad2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S55-guard')
print('✅', done)

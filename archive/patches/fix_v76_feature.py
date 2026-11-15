import ast, os
done = []
T = {
'missed.txt': "Hi {name}, Sundeep Rana here from Sunsoft Technology. 📞\nI tried calling you today regarding the {position} role at {where}, but couldn't reach you.\nKindly share your updated CV in PDF format here, along with a good time to reconnect. 🙏\nRegards,\nSundeep Rana",
'jd.txt': "Hi {name}, this is Sundeep Rana from Sunsoft Technology. 👋\nI have shared the job description for the {position} role at {where} on your email. 📄\nKindly check it, acknowledge receipt, and share your updated CV in PDF format for consideration.\nRegards,\nSundeep Rana",
'awaiting.txt': "Hi {name}, Sundeep Rana here. ⏰\nA gentle reminder regarding the job description I shared for the {position} role at {where}.\nWe are about to submit the first lot of candidates to the client, so kindly acknowledge today if you are interested to proceed.\nRegards,\nSundeep Rana",
'touch.txt': "Hi {name}, Sundeep Rana here from Sunsoft Technology. 👋\nHope you are doing well. I am keeping you in mind for roles like {position} at {where}.\nWhenever convenient, do share any update on your search or your latest CV. 🤝\nRegards,\nSundeep Rana",
'rejected.txt': "Hi {name}, thank you for your time and interest in the {position} role at {where}. 🙏\nThe client has chosen to move ahead with other profiles for now - this is not a reflection on you.\nI would love to stay in touch for future matches that fit your profile. Wishing you the very best! ✨\nRegards,\nSundeep Rana",
'reference.txt': "Hi {name}, Sundeep Rana here. Thank you for the honest reply earlier. 🙏\nAs discussed, I have shared the {position} details at {where} with you on WhatsApp.\nWhenever convenient, kindly share one or two referrals who may be a good fit - I would be truly grateful. 🤝\nRegards,\nSundeep Rana",
'outbox.txt': "Hi {name}, Sundeep Rana here from Sunsoft Technology. ✉️\nI am following up on my last message regarding the {position} role at {where}.\nA quick update from you will help me proceed or close the loop gracefully.\nRegards,\nSundeep Rana",
'interview.txt': "Hi {name}, Sundeep Rana here. Wishing you the very best for your {position} interview! 🍀\nPlease reach ten minutes early with a copy of your CV, and message me once you are done. 💬\nI am right here if you need anything at all.\nRegards,\nSundeep Rana",
'feedback.txt': "Hi {name}, Sundeep Rana here. I hope your {position} interview went well! 💬\nCould you kindly share how it went and any feedback you received?\nI will follow up with the client today and keep you posted on next steps. 🤞\nRegards,\nSundeep Rana",
}
os.makedirs('templates', exist_ok=True)
for f, body in T.items():
    open(os.path.join('templates', f), 'w').write(body + '\n')
open('wa_template.txt', 'w').write(T['missed.txt'] + '\n')
done.append(f'unified-voice-x{len(T)}+default')
F = open('briefing.py').read()
oldw = '    where = f"Company: {cli}" + (f" | Location: {loc}" if loc else "")'
if oldw in F and 'where=at' not in F:
    F = F.replace(oldw, oldw + '\n    at = cli + (f", {loc}" if loc else "")', 1)
    F = F.replace("return tpl.format(name=name, position=title, company=cli, location=loc or '-', where_line=where)",
                  "return tpl.format(name=name, position=title, company=cli, location=loc or '-', where_line=where, where=at)", 1)
    done.append('fmt-tpl-where')
if 'DEFAULT_TPL = (' in F and "couldn't reach you." not in F:
    i = F.index('DEFAULT_TPL = (')
    j = F.index('Thanks!")', i) + len('Thanks!")')
    F = F[:i] + ('DEFAULT_TPL = ("Hi {name}, Sundeep Rana here from Sunsoft Technology. 📞\\n"\n'
                 '"I tried calling you today regarding the {position} role at {where}, but couldn\'t reach you.\\n"\n'
                 '"Kindly share your updated CV in PDF format here, along with a good time to reconnect. 🙏\\n"\n'
                 '"Regards,\\nSundeep Rana")') + F[j:]
    done.append('default-tpl-voice')
open('briefing.py', 'w').write(F); ast.parse(F)
B = open('butler.py').read().split('\n')
if "'S57 unified voice + emojis" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S56 log trim + single helper defs" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "_tm = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'missed.txt')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'missed.txt')) else ''")
    B.insert(i+2, d*' ' + "ck('S57 unified voice + emojis', 'Regards,' in _tm and '📞' in _tm and 'where=at' in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S57-guard')
print('✅', done)

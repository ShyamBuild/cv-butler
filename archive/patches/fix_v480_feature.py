import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
if P.insert_before(B, 'def _eyename_of(', [(0, "_NAME_STOP = set('curriculum vitae resume summary profile objective challenging competitive dynamic results result oriented driven seeking looking opportunity position positions role roles manager engineer executive officer head director specialist consultant trainee intern fresher experienced professional personal contact educational education employment work experience skills strengths achievements awards certifications languages hobbies interests references address phone mobile email tel date birth age sex gender marital nationality indian india passport aadhar pan number ltd limited pvt inc co company companies industries industry technologies technology solutions services group corporation firm associates partners llc llp details information declaration father husband wife name'.split())  # NAME-GATE v85.97: a motto is not a man - any line touching the vocabulary of CVs-that-are-not-names is refused as a candidate")], once_marker='_NAME_STOP ='):
    done.append('name-stop-const')
n = P.sub_in_line(B, "if 2 <= len(_wsc) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in _wsc) and (_canonical_person_name(_cut) or ''):",
                  "if 2 <= len(_wsc) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in _wsc) and not (set(w.lower() for w in _wsc) & _NAME_STOP) and (_canonical_person_name(_cut) or ''):",
                  'NAME-GATE v85.97: the scanning eye refuses slogan-lines, so Challenging And Competitive can never again wear a man\'s coat')
if n: done.append('name-gate-x%d' % n)
n2 = P.sub_in_line(B, "_EYE_VSN = 'v85.96'", "_EYE_VSN = 'v85.97'", 'NAME-GATE v85.97: bump - the slogan verdicts cached under v85.96 expire at once')
if n2: done.append('eyevsn-bump')
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B)
P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.97' not in t:
    open(AR, 'a').write('v85.97: NAME-GATE - the scanning eye refuses any candidate line touching _NAME_STOP (CV vocabulary, slogans, roles, company words) after the sweep renamed Chandn.pdf to a slogan; eye-cache version bumped to void the wrong verdicts; the house may refuse but may not invent (S440)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S440 a motto never wears a man's coat", "'S439 a cached blindness expires the day the logic learns", "ck('S440 a motto never wears a man'+chr(39)+'s coat', ('_NAME_STOP' in _src) and (chr(35)+' NAME-GATE v85.97') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)

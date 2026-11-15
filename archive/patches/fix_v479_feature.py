import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
if P.insert_before(B, 'def _eyename_cache():', [(0, "_EYE_VSN = 'v85.96'  # EYECACHE-VSN v85.96: cached verdicts wear the version of the logic that made them")], once_marker='_EYE_VSN ='):
    done.append('eyecache-const')
n = P.sub_in_line(B, "if e and e[0] == st.st_size and abs(e[1] - st.st_mtime) < 1:",
                  "if e and len(e) > 3 and e[3] == _EYE_VSN and e[0] == st.st_size and abs(e[1] - st.st_mtime) < 1:",
                  'EYECACHE-VSN v85.96: a naming-logic change invalidates every cached verdict, so stale blindness cannot outlive its cure')
n += P.sub_in_line(B, "c[key] = [st.st_size, st.st_mtime, name]",
                   "c[key] = [st.st_size, st.st_mtime, name, _EYE_VSN]",
                   'EYECACHE-VSN v85.96: the verdict carries its logic version into the book')
if n: done.append('eyecache-vsn-x%d' % n)
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B)
P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.96' not in t:
    open(AR, 'a').write('v85.96: EYECACHE-VSN - cached eye verdicts carry the naming-logic version and a hit requires the current one, curing the stale empty verdict that kept Chandn.pdf blind after NAME-SCAN landed; the cache can never again forbid a day the house learns (S439)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S439 a cached blindness expires the day the logic learns", "'S438 a name below the first line is still a name", "ck('S439 a cached blindness expires the day the logic learns', _src.count('_EYE_VSN') >= 3)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)

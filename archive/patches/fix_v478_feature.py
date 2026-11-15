import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
n1 = P.sub_in_line(B, "r = subprocess.run([OCRBIN, _tgt], capture_output=True, text=True, timeout=25)",
                      "r = subprocess.run([OCRBIN, _tgt, 'stdout'], capture_output=True, text=True, timeout=25)",
                      'OCR-STDOUT v85.95: tesseract needs an outputbase and stdout is the word - for months the eye handed an image and no destination, and read usage text')
if n1: done.append('ocr-stdout-x%d' % n1)
lc = next((k for k, l in enumerate(B) if 'LINE-CUT v85.90' in l), None)
if lc is not None and 'NAME-SCAN v85.95' not in '\n'.join(B[lc-8:lc]):
    d = P.ind(B[lc])
    B[lc-6:lc] = [d*' ' + "fl = ''",
                  d*' ' + "_lines = [l.strip() for l in t.split('\\n') if l.strip()][:12]  # NAME-SCAN v85.95: a name may sit below a title line or a photo caption - scan the head, not just the first breath",
                  d*' ' + "for _ln in _lines:",
                  (d+4)*' ' + "_cut = re.split(r'\\s+(?:Phone|Mob|Tel|E-Mail|Email)[:\\-]?', _ln, flags=re.I)[0].strip()",
                  (d+4)*' ' + "_wsc = _cut.split()",
                  (d+4)*' ' + "if 2 <= len(_wsc) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in _wsc) and (_canonical_person_name(_cut) or ''):",
                  (d+8)*' ' + "fl = _cut",
                  (d+8)*' ' + "break",
                  d*' ' + "if not fl and _lines: fl = _lines[0]"]
    done.append('name-scan')
n2 = P.sub_in_line(B, "try: v = heuristic_name(p) or _name_from_first_line(p)",
                    "try: v = heuristic_name(p) or _name_from_first_line(p) or _eyename_of(p)",
                    'NAME-SCAN-SERVICE v85.95: the right-click borrows the scanning eye and its cache, so a photo-headed CV is named from its own head')
if n2: done.append('name-scan-service-x%d' % n2)
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B)
P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.95' not in t:
    open(AR, 'a').write('v85.95: OCR-STDOUT gives tesseract its outputbase so the capped eye reads scans at last (it read usage text for months); NAME-SCAN lets the cached eye take the first canonisable line among the head twelve, curing photo-headed CVs like Chandn; the service borrows the scanning eye (S437, S438)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S437 the capped eye names its destination, and reads", "'S436 a bad lap dies childless, before any file is written", "ck('S437 the capped eye names its destination, and reads', (chr(35)+' OCR-STDOUT v85.95') in _src and (chr(39)+'stdout'+chr(39) in _src))"),
      ("'S438 a name below the first line is still a name", "'S437 the capped eye names its destination, and reads", "ck('S438 a name below the first line is still a name', (chr(35)+' NAME-SCAN v85.95') in _src and (chr(35)+' NAME-SCAN-SERVICE v85.95') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)

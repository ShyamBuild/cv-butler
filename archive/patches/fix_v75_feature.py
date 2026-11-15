done = []
S = open('ship.sh').read()
if 'cadence.py' not in S:
    S = S.replace('"$HOME/CV_Tool/ledger.py" "$HOME/CV_Tool_pub/"',
                  '"$HOME/CV_Tool/ledger.py" "$HOME/CV_Tool/cadence.py" "$HOME/CV_Tool/sem.py" "$HOME/CV_Tool/waread.py" "$HOME/CV_Tool_pub/"')
    done.append('mirror-modules')
if 'templates/' not in S:
    S = S.replace('git -C "$HOME/CV_Tool_pub" add -A || return 0',
                  'cp "$HOME/CV_Tool/wa_template.txt" "$HOME/CV_Tool_pub/" 2>/dev/null\n  mkdir -p "$HOME/CV_Tool_pub/templates"\n  cp "$HOME/CV_Tool/templates/"*.txt "$HOME/CV_Tool_pub/templates/" 2>/dev/null\n  git -C "$HOME/CV_Tool_pub" add -A || return 0')
    done.append('mirror-templates')
open('ship.sh', 'w').write(S)
print('✅', done or 'nothing missing')

#!/bin/zsh
~/CV_Tool/archive/mkdump.sh
echo "== dump lines: $(wc -l < ~/CV_Tool/archive/dump.txt)"
echo "== health"; butler health 2>/dev/null | tail -4
echo "== tick tail"; tail -6 ~/CV_Tool/tick.log 2>/dev/null
echo "== rendiag head"; ~/CV_Tool/cv_env/bin/python3 ~/CV_Tool/archive/rendiag.py 2>/dev/null | head -4
echo "== sources head"; sed -n '1,30p' ~/CV_Tool/archive/dump.txt

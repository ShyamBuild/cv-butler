# BUTLER DEVELOPMENT PROTOCOL - follow every time, any model, any human
1. TRUTH: ~/CV_Tool/butler.py + briefing.py are live. git = memory. Last commit = last proven state.
2. NEVER hand-edit live files. A change arrives as a patch script (fix_*.py): read -> transform -> ast.parse -> write.
3. DEPLOY ONLY VIA:  ./ship.sh "vN: what changed" ~/fix_*.py
   ship.sh = patch -> selftest S1-S5 + twin-folder check -> ALL GREEN: git commit + auto background restart.
   NOT GREEN: ship.sh auto-rolls back live files to last commit and prints FAILs. Broken code never stays.
4. SKILLS (selftest in butler.py --selftest): S1 class bindings · S2 tag reading · S3 tag-driven move ·
   S4 wrong-name repair · S5 board row. NEW SKILL = new S-test written FIRST, then the code that passes it.
5. VERSIONS: git log --oneline. ROLLBACK: git checkout <hash> -- butler.py briefing.py, then ./ship.sh "revert: ...".
6. REVIEW HANDOFF: paste `git log --oneline | head -20` plus `git diff <old>..<new> -- butler.py briefing.py`
   and any reviewer (Sundeep or another AI) can audit exactly what changed between proven states.
7. FORBIDDEN: editing live files without a patch script · committing without ALL GREEN · two butlers on
   overlapping folders · permanent deletes (cleaner is Trash-only) · inline # comments in terminal commands.
8. RUNTIME: butler runs in background after each green commit. Watch: tail -f butler_live.log ·
   Commands/chat: cv_env/bin/python3 briefing.py chat · Stop: pkill -f butler.py · Manual restart: ./ship.sh "restart-only" (no patch).
9. FORBIDDEN: blanket 'self. -> B.' rewrites by rule. Nested classes (watchdog H inside main) are
   outside class Butler but NEED self. Fix self/B bugs surgically, one named block at a time.

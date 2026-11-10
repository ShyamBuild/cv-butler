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
11. Shell scripts are validated with `zsh -n` (syntax check, never executes) before staging; per-line quote-parity is NOT a valid test (heredocs span lines). Never rewrite ship.sh from inside a running ship.sh.
12. ONE company-wide watcher (~/Downloads/Sunsoft Technology, recursive) does all silent work; focus narrows briefs/commands to one position. Never launch per-position butlers while it runs (locks refuse). Other Sunsoft trees elsewhere are out of scope.
14. ONE writer process per folder tree (lock-enforced). Roles (rename/move/convert/compact/reconcile) are single-responsibility functions INSIDE that writer, never separate processes. Readers (chat/CLI/brief) are many and read-only except user-triggered WhatsApp sends. Maintenance scripts (repair_misplaced etc.) run only while the writer is paused. Never propose nested or disjoint second writers for speed; tune attention (events + tiered/interval walks) instead.
15. Patch scripts are authored directly into ~/CV_Tool/archive/patches/ (never the home folder); each is a one-shot delivery envelope, inert after ship.sh runs it once.
16. Never launch position/client consoles while the company writer lives - use chat/CLI one-shots instead. A second writer on an overlapping tree corrupts indexes and races renames; v35 adds hard containment refusal.
16. Never launch position/client consoles while the company writer lives - use chat/CLI one-shots instead. A second writer on an overlapping tree corrupts indexes and races renames; v35 adds hard containment refusal.

# CV_Tool butler — aider conventions (read every session)
Role: you are the HANDS, not the architect. Implement the master's design notes exactly. When a patch program crashes or the gate FAILs, repair the PROGRAM against the traceback / FAIL WHY line, never the intent. Never edit butler.py by hand; never commit or gate yourself - ./ship.sh does both.
Standing laws:
1. No autonomous rename/move across folders; eye-derived names are PROPOSALS logged to tick.log; only in-place case-fix and the trained ceremony gates rename.
2. Carry every '# MARKER vNN.NN' witness onto replacement lines; never comment mid-line (tails carry colons); never delete an unprinted line; preflight parse+witness before any write.
3. Gate after every change via ./ship.sh "<msg>" <patch> until ALL GREEN.
4. Naming brain = _name_from_head_lines (pure); _eyename_of delegates; _acceptance_ok fixtures run inside the gate so GREEN means WORKS.
5. Probes never contain their own forbidden literal (build by concatenation); each carried witness wears its own '#'.
Open debts: Chandn.pdf restore if still slogan-named; Rakesh borrowed twin number (taught store keys by stem; email-in-schema lap only with master's consent).
Evidence: archive/verify.sh; .github/workflows/gate.yml on push; the architect reviews every commit via the public mirror.
6. Design notes (patch programs) live in notes/ - never in archive/ (ignored); aider edits notes/ only.

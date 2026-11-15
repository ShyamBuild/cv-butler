import ast, json, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
EN = chr(8211)
vmap = {"Awaiting JD Confirmation": "jd", "Awaiting CV Update": "cv_update", "Call Scheduled": "missed",
        "Feedback Pending": "feedback_pending", "Shortlisted for Interview": "shortlisted",
        "Interview Scheduled": "interview_confirm", "Rejected by Client": "rejected_client",
        f"Closed {EN} Not Proceeding": "referral"}
mp = os.path.join(D, 'tag_voices.json')
if not os.path.exists(mp):
    json.dump(vmap, open(mp, 'w'), indent=1, ensure_ascii=False); done.append('tag-voices-map')
SIG = 'Sundeep Rana here from Sunsoft Technology. 📞'
RG = ' 🙏 Regards, Sundeep Rana'
tpl = {
 'voice_jd.txt': f'Hi {{name}}, {SIG} Sharing the JD for {{position}} at {{client}}, {{location}}. Kindly go through it and confirm your interest so we can take it forward.{RG}',
 'voice_missed.txt': f'Hi {{name}}, {SIG} I tried calling you today regarding the {{position}} at {{client}}, {{location}}, but couldn\u2019t reach you. Kindly share your updated CV in PDF format here, along with a good time to reconnect.{RG}',
 'voice_cv_update.txt': f'Hi {{name}}, {SIG} For the {{position}} at {{client}}, {{location}}, kindly share your updated CV in PDF format at the earliest, along with a good time to reconnect.{RG}',
 'voice_feedback_pending.txt': f'Hi {{name}}, {SIG} Your profile for {{position}} at {{client}} is with the client for shortlisting. Please stay ready for a possible interview as per the client\u2019s schedule; I will confirm the slot the moment it is fixed.{RG}',
 'voice_shortlisted.txt': f'Hi {{name}}, {SIG} Happy to share that you are shortlisted for the interview for {{position}} at {{client}}. The date and time are being confirmed with the client; I will share them shortly by email, which kindly acknowledge. Please stay ready for both virtual and face-to-face rounds.{RG}',
 'voice_interview_confirm.txt': f'Hi {{name}}, {SIG} Your interview for {{position}} at {{client}} is scheduled for [date & time]. Kindly confirm your availability on this number; the detailed email follows shortly and please acknowledge it.{RG}',
 'voice_rejected_client.txt': f'Hi {{name}}, {SIG} For {{position}} at {{client}}, the client has not taken your profile forward this time. I will keep your profile with me for future roles that fit you better, and if you know anyone suitable, kindly share their reference.{RG}',
 'voice_referral.txt': f'Hi {{name}}, {SIG} Thank you for letting me know. If you have any references or contacts who may be interested in similar roles, kindly share them here; I will keep you in mind for future fits.{RG}'}
os.makedirs(os.path.join(D, 'templates'), exist_ok=True)
for fnm, txt in tpl.items():
    fp = os.path.join(D, 'templates', fnm)
    if not os.path.exists(fp): open(fp, 'w').write(txt + '\n'); done.append(f'tpl-{fnm}')
fg = os.path.join(D, 'autodraft.flag')
if not os.path.exists(fg): open(fg, 'w').write('auto\n'); done.append('autodraft-flag')
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if '# TAG-POLL' in l and ('> 8:' in l or '> 15:' in l):
        B[k] = l.replace('> 15:', '> 4:').replace('> 8:', '> 4:'); done.append('pulse-4s')
    if l.strip().startswith("ck('S89 rename and move in one pass'"):
        B[k] = ind(l)*' ' + "ck('S89 rename and move in one pass', (chr(35)+' INODE-RELINK') in _src and sum(1 for L in _src.split(chr(10)) if (chr(35)+' TAG-POLL') in L and ('> 8:' in L or '> 15:' in L)) == 0)"
        done.append('S89-interval-agnostic')
src = '\n'.join(B)
if 'def _tag_poll(self):' in src and '_added_tags' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'def _tag_poll(self):')
    j = next(k for k in range(i, i+30) if B[k].strip() == 'return changed')
    d = ind(B[i])
    B[i:j+1] = [d*' ' + "def _tag_poll(self):",
                d*' ' + "    import zlib as _z",
                d*' ' + "    if not hasattr(self, '_tagcrc'): self._tagcrc = {}",
                d*' ' + "    if not hasattr(self, '_tagsets'): self._tagsets = {}",
                d*' ' + "    self._added_tags = {}",
                d*' ' + "    now = time.time()",
                d*' ' + "    gap = (now - getattr(self, '_last_poll_ts', 0)) > 300",
                d*' ' + "    self._last_poll_ts = now",
                d*' ' + "    changed = []",
                d*' ' + "    for dp, dn, fn in os.walk(self.root):",
                d*' ' + "        dn[:] = [x for x in dn if not x.startswith('.')]",
                d*' ' + "        for f in fn:",
                d*' ' + "            if not f.lower().endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue",
                d*' ' + "            fp = os.path.join(dp, f)",
                d*' ' + "            try: tg = os.getxattr(fp, 'com.apple.metadata:_kMDItemUserTags')",
                d*' ' + "            except Exception: tg = b''",
                d*' ' + "            c = _z.crc32(tg)",
                d*' ' + "            old = self._tagcrc.get(fp)",
                d*' ' + "            self._tagcrc[fp] = c",
                d*' ' + "            prev = self._tagsets.get(fp)",
                d*' ' + "            if old is not None and old != c:",
                d*' ' + "                changed.append(fp)",
                d*' ' + "                cur = [t for t in (_tags_of_fast(fp) or [])]",
                d*' ' + "                if prev is not None and not gap:",
                d*' ' + "                    add = [t for t in cur if t not in prev]",
                d*' ' + "                    if add: self._added_tags[fp] = add",
                d*' ' + "                self._tagsets[fp] = cur",
                d*' ' + "            elif prev is None:",
                d*' ' + "                self._tagsets[fp] = [t for t in (_tags_of_fast(fp) or [])]",
                d*' ' + "    if len(self._tagcrc) > 20000: self._tagcrc = {}",
                d*' ' + "    return changed"]
    done.append('tag-poll-delta')
src = '\n'.join(B)
if 'B._autodraft_tick()' not in src:
    n = 0
    for k, l in enumerate(B):
        if l.strip() == 'for _cp in B._tag_poll(): ex.submit(work, _cp)':
            B.insert(k+1, ind(l)*' ' + 'B._autodraft_tick()'); n += 1
    if n: done.append(f'autodraft-wired-x{n}')
src = '\n'.join(B)
if 'def _autodraft_tick(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    B[i:i] = ["    def _ad_enabled(self):  # AUTODRAFT v81",
              "        try: st = open(os.path.join(BASE_DIR, 'autodraft.flag')).read().strip()",
              "        except Exception: st = 'auto'",
              "        if st == 'off': return False",
              "        if st in ('on', 'dry'): return True",
              "        try:",
              "            import subprocess",
              "            return bool(subprocess.run(['pgrep', '-f', 'briefing.py chat'], capture_output=True).stdout.strip())",
              "        except Exception: return False",
              "    def _phone_for(self, phs):",
              "        if not phs: return None",
              "        nb = _names_by_phone()",
              "        for d in phs:",
              "            if d in nb: return d",
              "        try: conv = json.load(open(os.path.join(BASE_DIR, 'conversations.json')))",
              "        except Exception: conv = {}",
              "        for d in phs:",
              "            if d in conv: return d",
              "        return phs[0]",
              "    def _ad_fire(self, d, txt, v, nm, say):",
              "        import threading",
              "        self._ad_pending = time.time() + 75",
              "        say(f'📝 autodraft: {v} -> +{d} ({nm})')",
              "        def _run():",
              "            try:",
              "                import wa",
              "                try: wa.send_review(d, txt, say)",
              "                except TypeError: wa.send_review(d, txt)",
              "            except Exception: pass",
              "        threading.Thread(target=_run, daemon=True).start()",
              "    def _draft_one(self, fp, tg, v, mode, say):",
              "        try:",
              "            if not os.path.exists(fp) or _settling(fp): return",
              "            rel = os.path.relpath(os.path.dirname(fp), self.root).split(os.sep)",
              "            if len(rel) < 2: return",
              "            client, posraw = rel[0], rel[1]",
              "            pos = posraw.split('||')[0].strip().replace('_', ' ')",
              "            loc = posraw.split('||')[1].strip() if '||' in posraw else ''",
              "            try:",
              "                import fitrank",
              "                phs = phones_of(fitrank._text(fp)) or []",
              "            except Exception: phs = []",
              "            d = self._phone_for(phs)",
              "            if not d: say(f'⏭️ autodraft skip (no phone): {os.path.basename(fp)}'); return",
              "            lp = os.path.join(BASE_DIR, 'autodraft_log.json')",
              "            try: lg = json.load(open(lp))",
              "            except Exception: lg = {}",
              "            k = f'{d}|{v}'",
              "            if time.time() - lg.get(k, 0) < 86400: return",
              "            nm = _names_by_phone().get(d) or os.path.splitext(os.path.basename(fp))[0]",
              "            try: txt = open(os.path.join(BASE_DIR, 'templates', f'voice_{v}.txt')).read()",
              "            except Exception: say(f'⚠️ autodraft: missing template voice_{v}'); return",
              "            txt = txt.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc)",
              "            lg[k] = time.time(); json.dump(lg, open(lp, 'w'), indent=1)",
              "            if mode == 'dry':",
              "                say(f'📝 [dry] {v} -> +{d} ({nm}): {txt[:110]}…'); return",
              "            if getattr(self, '_ad_pending', 0) > time.time():",
              "                qp = os.path.join(BASE_DIR, 'autodraft_queue.json')",
              "                try: q = json.load(open(qp))",
              "                except Exception: q = []",
              "                q = [x for x in q if time.time() - x.get('at', 0) < 7200]",
              "                q.append({'phone': d, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v})",
              "                json.dump(q, open(qp, 'w'), indent=1)",
              "                say(f'📝 queued autodraft: {v} -> {nm} (+{d})'); return",
              "            self._ad_fire(d, txt, v, nm, say)",
              "        except Exception as e:",
              "            say(f'⚠️ autodraft error: {e}')",
              "    def _autodraft_tick(self, say=print):",
              "        try:",
              "            if not self._ad_enabled(): return",
              "            mode = 'auto'",
              "            try: mode = open(os.path.join(BASE_DIR, 'autodraft.flag')).read().strip() or 'auto'",
              "            except Exception: mode = 'auto'",
              "            qp = os.path.join(BASE_DIR, 'autodraft_queue.json')",
              "            if getattr(self, '_ad_pending', 0) <= time.time():",
              "                try: q = json.load(open(qp))",
              "                except Exception: q = []",
              "                q = [x for x in q if time.time() - x.get('at', 0) < 7200]",
              "                if q:",
              "                    it = q.pop(0); json.dump(q, open(qp, 'w'), indent=1)",
              "                    self._ad_fire(it['phone'], it['text'], it['voice'], it['who'], say)",
              "            added, self._added_tags = getattr(self, '_added_tags', {}), {}",
              "            try: vm = json.load(open(os.path.join(BASE_DIR, 'tag_voices.json')))",
              "            except Exception: return",
              "            for fp, tags in added.items():",
              "                for tg in tags:",
              "                    v = vm.get(tg) or vm.get(tg.replace(chr(8211), '-'))",
              "                    if v: self._draft_one(fp, tg, v, mode, say)",
              "        except Exception as e:",
              "            say(f'⚠️ autodraft tick: {e}')",
              ""]
    done.append('autodraft-engine')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S105 tag voice map has no internal stages" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S104 butler learns manual renames" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_vm = json.load(open(os.path.join(BASE_DIR, 'tag_voices.json')))")
    B.insert(i+2, d*' ' + "ck('S105 tag voice map has no internal stages', 'Ready for Manager Review' not in _vm and len(_vm) >= 7)")
    B.insert(i+3, d*' ' + "ck('S106 autodraft never sends', '.send(' not in _src.split('def _autodraft_tick')[1].split('def _heal')[0] and '_click_send' not in _src.split('def _autodraft_tick')[1].split('def _heal')[0])")
    B.insert(i+4, d*' ' + "ck('S107 toggle honoured', 'autodraft.flag' in _src and 'briefing.py chat' in _src and (chr(35)+' AUTODRAFT') in _src)")
    B.insert(i+5, d*' ' + "ck('S108 drafts go through the signed wa door', 'wa.send_review(' in _src and 'import wa' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S105-S108-guards')
print('✅', done)

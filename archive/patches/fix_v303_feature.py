import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _auto_registry(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _errands_tick('))
    B[i:i] = ["    def _auto_registry(self, say=print):  # AUTO-REG v84.22: a new position folder is understood the moment it lands; a new client asks for its company once",
              "        try:",
              "            root = _pl_root()",
              "            try: reg = json.load(open(POS_PATH))",
              "            except Exception: reg = {}",
              "            spoken = reg.get('__spoken__', {})",
              "            try: cm = json.load(open(CLIENTMAP_PATH))",
              "            except Exception: cm = {}",
              "            changed = False",
              "            for client in os.listdir(root):",
              "                cp = os.path.join(root, client)",
              "                if client.startswith('.') or not os.path.isdir(cp): continue",
              "                for pos in os.listdir(cp):",
              "                    pp = os.path.join(cp, pos)",
              "                    if pos.startswith('.') or not os.path.isdir(pp): continue",
              "                    if pp not in reg:",
              "                        role, loc = (pos.split(' -', 1) + [''])[:2]",
              "                        reg[pp] = {'company': cm.get(client, ''), 'role': role.strip(), 'loc': loc.strip(), 'designation': ''}",
              "                        changed = True",
              "                        say(f'🧠 new position understood: {client} / {pos}' + ('' if cm.get(client) else ' - company unknown; teach once: client ' + client + ' = <company>'))",
              "                    elif not reg[pp].get('company') and cm.get(client):",
              "                        reg[pp]['company'] = cm[client]; changed = True",
              "                if client not in cm and client not in spoken:",
              "                    spoken[client] = int(time.time()); changed = True",
              "                    say(f'🏢 new client folder: {client} - teach me once: client {client} = <company>')",
              "            reg['__spoken__'] = spoken",
              "            if changed: json.dump(reg, open(POS_PATH, 'w'), indent=1)",
              "        except Exception:",
              "            pass",
              ""]
    done.append('auto-reg')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('self._errands_tick(say)') and '_auto_registry' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "self._auto_registry(say)  # AUTO-REG v84.22: the registry grows while the sweep works")
        done.append('auto-reg-hook'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip() == "out = {'company': '', 'role': '', 'loc': ''}":
        B[k] = ind(l)*' ' + "out = {'company': '', 'role': '', 'loc': '', 'designation': ''}  # DESIGNATION v84.22"
        done.append('designation-field'); break
for k, l in enumerate(B):
    if l.strip().startswith("out['loc'] = ov.get('loc') or loc.strip()") and 'designation' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "out['designation'] = ov.get('designation') or ''")
        done.append('designation-read'); break
for k, l in enumerate(B):
    if l.strip().startswith("if len(parts) > 1 and parts[1]: ov['role'] = parts[1]"):
        B[k] = ind(l)*' ' + "if len(parts) > 1 and parts[1]: ov['designation'] = parts[1]  # DESIGNATION v84.22: the middle slot is the designation, not the folder's role"
        done.append('posmeta-designation'); break
r0 = next(k for k, l in enumerate(B) if l.strip() == '_rl = []')
r1 = next(k for k in range(r0, len(B)) if l.strip().startswith('roleline = ') for l in [B[k]])
B[r0:r1+1] = ["    _dz = _idn['designation'] or _idn['role']",
              "    _co = _idn['company'] or meta.get('company')",
              "    _parts = []",
              "    if _dz: _parts.append('the ' + _dz + ' opening')",
              "    if _co: _parts.append('for ' + _co)",
              "    _tail = ', '.join(x for x in (_idn['role'], _idn['loc']) if x and x != _dz)",
              "    if _tail: _parts.append('(' + _tail + ')')",
              "    roleline = ' '.join(_parts) or 'the role we discussed'  # ROLELINE v84.18 (refined v84.22): designation, company, then where - omitting only what was never taught"]
done.append('roleline-refined')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S278 a new position is understood the moment it lands, a new client asks once", "'S277 the chair shows the triple before the thumb decides", "ck('S278 a new position is understood the moment it lands, a new client asks once', (chr(35)+' AUTO-REG v84.22') in _src and ('def _auto_registry(' in _src))"),
      ("'S279 the roleline speaks designation, company, role and location in one clause", "'S278 a new position is understood the moment it lands, a new client asks once", "ck('S279 the roleline speaks designation, company, role and location in one clause', (chr(35)+' DESIGNATION v84.22') in _src and (\"'designation'\" in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)

"""Conservative, tag-gated update of an existing client summary workbook."""
import datetime as dt
import os
import re
import shutil
import tempfile
import threading

SUMMARY_LOCK = threading.RLock()
READY_TAG = "ready for manager review"
READY_FOLDER = "ready for manager review"
FIELD_LABELS = {
    "total experience": ("total experience", "work experience in yrs", "work experience", "experience"),
    "current ctc": ("current ctc", "present ctc"),
    "expected ctc": ("expected ctc",),
    "present location": ("present location", "current location"),
    "permanent location": ("permanent location", "preferred location", "preferred locations"),
    "notice period": ("notice period",),
}
HEADER_ALIASES = {
    "candidate name": {"candidate name"},
    "position": {"position", "role", "job title"},
    "age": {"age", "age in years"},
    "date": {"date", "date of sharing", "submission date"},
    "s no": {"s no", "s no.", "s.no", "s.no."},
    "total experience": {"total experience", "work experience in yrs", "work experience", "experience"},
    "current ctc": {"current ctc", "present ctc"},
    "expected ctc": {"expected ctc"},
    "present location": {"present location", "current location"},
    "permanent location": {"permanent location", "preferred location", "preferred locations"},
    "notice period": {"notice period"},
    "contact no": {"contact no", "contact no.", "contact number", "phone", "mobile"},
    "email id": {"email id", "email"},
}


def _norm(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").strip().lower()).strip()


def _canonical_tag(tag):
    return _norm(str(tag).splitlines()[0])


def eligible_pdf(path, tags):
    return (str(path).lower().endswith(".pdf")
            and os.path.basename(os.path.dirname(os.path.abspath(path))).strip().lower() == READY_FOLDER
            and any(_canonical_tag(tag) == READY_TAG for tag in (tags or [])))


def extract_sunsoft_fields(pdf_path):
    """Read explicit Sunsoft annotation values only; never infer call data."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path, strict=False)
    except Exception as exc:
        return {}, "pdf_unreadable: " + str(exc)
    block = ""
    try:
        for page in reader.pages:
            for ref in page.get("/Annots") or []:
                annot = ref.get_object()
                content = str(annot.get("/Contents") or "").strip()
                if content.lower().startswith("sunsoft technology"):
                    block = content
                    break
            if block:
                break
    except Exception as exc:
        return {}, "annotation_unreadable: " + str(exc)
    if not block:
        return {}, "missing_sunsoft_annotation"
    values = {}
    for line in block.splitlines()[1:]:
        if ":" not in line:
            continue
        label, value = line.split(":", 1)
        key = _norm(label)
        value = value.strip()
        if value:
            values[key] = value
    return values, None


def _first_pdf_text(pdf_path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path, strict=False)
        return "\n".join((page.extract_text() or "") for page in reader.pages[:5])
    except Exception:
        return ""


def _find_value(text, pattern):
    match = re.search(pattern, text or "", re.I)
    return match.group(1).strip() if match else None


def _estimated_age(text, today=None):
    day = today or dt.date.today()
    dob = re.search(r"(?:date\\s+of\\s+birth|birth\\s+date|\\bdob\\b)\\s*[:\\-]?\\s*(.{3,24})", text or "", re.I)
    if dob:
        value = dob.group(1).splitlines()[0].strip(" .,-")
        for fmt in ("%d %B %Y", "%d %b %Y", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"):
            try:
                born = dt.datetime.strptime(value, fmt).date()
                age = day.year - born.year - ((day.month, day.day) < (born.month, born.day))
                if 15 <= age <= 70: return str(age) + " years"
            except ValueError: pass
    estimates=[]
    patterns=((r"(?:10th|matriculation|class\\s*x)\\D{0,70}?(?:passed|pass|year)?\\D{0,12}(20\\d{2}|19\\d{2})",15),
              (r"(?:12th|intermediate|higher\\s+secondary|class\\s*xii)\\D{0,70}?(?:passed|pass|year)?\\D{0,12}(20\\d{2}|19\\d{2})",17))
    for pattern,baseline in patterns:
        for match in re.finditer(pattern,text or "",re.I):
            year=int(match.group(1))
            if 1960<=year<=day.year: estimates.append(day.year-year+baseline)
    if not estimates:return None
    return "~%d years (education-based estimate)" % max(15,min(70,round(sum(estimates)/len(estimates))))


def _candidate_fields(pdf_path, sunsoft, headers=None):
    stem = os.path.splitext(os.path.basename(pdf_path))[0].strip()
    text = _first_pdf_text(pdf_path)
    fields = {"candidate name": stem}
    for key, aliases in FIELD_LABELS.items():
        value = next((sunsoft.get(_norm(alias)) for alias in aliases if sunsoft.get(_norm(alias))), None)
        if value:
            fields[key] = value
    email = _find_value(text, r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})")
    phone_match = re.search(r"(?<!\d)(?:\+?91[\s().-]*)?([6-9](?:[\s().-]*\d){9})(?!\d)", text)
    phone = re.sub(r"\D", "", phone_match.group(1)) if phone_match else None
    if email:
        fields["email id"] = email
    if phone and len(phone) == 10:
        fields["contact no"] = phone
    if headers and any(_norm(h) == 'age' for h in headers if h is not None):
        age = _estimated_age(text)
        if age: fields['age'] = age
    return fields


def _headers(ws):
    for rownum in range(1, min(6, ws.max_row) + 1):
        vals = [cell.value for cell in ws[rownum]]
        normalized = {_norm(v) for v in vals if v is not None}
        if "candidate name" in normalized:
            return rownum, vals
    return None, None


def _map_columns(headers):
    by_norm = {}
    for idx, header in enumerate(headers, 1):
        key = _norm(header)
        if key:
            by_norm.setdefault(key, idx)
    mapped = {}
    for field, aliases in HEADER_ALIASES.items():
        col = next((by_norm[_norm(alias)] for alias in aliases if _norm(alias) in by_norm), None)
        if col:
            mapped[field] = col
    return mapped


def _candidate_row(ws, header_row, name_col, name):
    target = _norm(name)
    for row in range(header_row + 1, ws.max_row + 1):
        value = ws.cell(row, name_col).value
        if value is not None and _norm(value) == target:
            return row
    return None


def _make_empty_template_copy(template, output):
    shutil.copy2(template, output)
    import openpyxl
    wb = openpyxl.load_workbook(output)
    ws = wb.active
    header, values = _headers(ws)
    if not header or 'candidate name' not in _map_columns(values):
        wb.close(); os.unlink(output)
        raise ValueError('template needs a Candidate Name column')
    name_col = _map_columns(values)['candidate name']
    for row in range(header + 1, ws.max_row + 1):
        # Clear candidate data but retain formatting and existing blank/template rows.
        if ws.cell(row, name_col).value is not None:
            for col in range(1, ws.max_column + 1): ws.cell(row, col).value = None
    wb.save(output); wb.close()
    return header


def _append_selected_summary_row(output, template, pdf, today=None, candidate_name=None):
    from copy import copy
    annotation, err = extract_sunsoft_fields(pdf)
    if err: return {'status':'skipped','reason':err}
    import openpyxl
    wb=openpyxl.load_workbook(output); ws=wb.active
    header, headers=_headers(ws); cols=_map_columns(headers)
    if not header or 'candidate name' not in cols:
        wb.close(); return {'status':'error','reason':'candidate name column missing'}
    fields=_candidate_fields(pdf,annotation,headers)
    if candidate_name: fields['candidate name']=candidate_name
    row=next((r for r in range(header+1,ws.max_row+1) if ws.cell(r,cols['candidate name']).value in (None,'')),ws.max_row+1)
    source=openpyxl.load_workbook(template); sws=source.active
    style_row=max(header+1,sws.max_row)
    for col in range(1,max(ws.max_column,sws.max_column)+1):
        a=sws.cell(style_row,col); b=ws.cell(row,col)
        if a.has_style: b._style=copy(a._style)
        if a.number_format: b.number_format=a.number_format
        if a.alignment: b.alignment=copy(a.alignment)
    values=dict(fields); values['date']=dt.datetime.combine(today or dt.date.today(),dt.time.min)
    if cols.get('s no'): values['s no']=row-header
    for key,col in cols.items():
        if values.get(key) is not None: ws.cell(row,col).value=values[key]
    temp=output+'.tmp'
    try: wb.save(temp); wb.close(); source.close(); os.replace(temp,output)
    except Exception as exc:
        try: wb.close(); source.close()
        except Exception: pass
        try: os.unlink(temp)
        except OSError: pass
        return {'status':'error','reason':str(exc)}
    return {'status':'added','candidate':fields['candidate name'],'row':row}


def build_selected_summary(paths, template, say=print, today=None, output_path=None, base_names=None, tags_by_path=None):
    selected=list(dict.fromkeys(os.path.abspath(os.path.expanduser(os.fspath(p))) for p in paths if str(p).lower().endswith('.pdf')))
    if not selected: return {'status':'error','reason':'select one or more PDF CVs'}
    folders={os.path.dirname(p) for p in selected}
    if len(folders)!=1: return {'status':'error','reason':'select CVs from one folder'}
    folder=next(iter(folders)); template=os.path.abspath(os.path.expanduser(template))
    if not os.path.isfile(template) or not template.lower().endswith('.xlsx'):
        return {'status':'error','reason':'choose an existing client .xlsx template'}
    output=os.path.abspath(output_path) if output_path else next_collision_path(folder,'Summary','.xlsx')
    if os.path.dirname(output)!=folder or os.path.exists(output): return {'status':'error','reason':'output must be a new workbook in selected folder'}
    try: _make_empty_template_copy(template,output)
    except Exception as exc: return {'status':'error','reason':'template copy failed: '+str(exc)}
    results=[]
    for pdf in selected:
        tags=(tags_by_path or {}).get(pdf)
        if tags is None:
            try:
                import butler
                tags=butler._tags_of_fast(pdf) or butler.get_tags(pdf)
            except Exception: tags=[]
        if not any(_canonical_tag(t)==READY_TAG for t in (tags or [])):
            result={'status':'skipped','reason':'Ready tag missing'}
        else:
            nm=(base_names or {}).get(pdf)
            result=_append_selected_summary_row(output,template,pdf,today,candidate_name=nm)
        results.append(result)
        if result.get('status')=='added': say('Summary row %s: %s'%(result['row'],result['candidate']))
        else: say('Skipped %s: %s'%(os.path.basename(pdf),result.get('reason')))
    count=sum(r.get('status')=='added' for r in results)
    if not count:
        try: os.unlink(output)
        except OSError: pass
        return {'status':'error','reason':'no selected tagged CV contained a Sunsoft annotation','results':results}
    return {'status':'created','summary':output,'count':count,'results':results}


def next_collision_path(folder, stem, extension):
    candidate = os.path.join(folder, stem + extension)
    if not os.path.exists(candidate): return candidate
    index=1
    while os.path.exists(os.path.join(folder, "%s_%d%s"%(stem,index,extension))): index+=1
    return os.path.join(folder, "%s_%d%s"%(stem,index,extension))


def _candidate_base_and_number(stem):
    m=re.fullmatch(r"(.+?)(?:_(\d+))?",stem.strip())
    if not m:return stem.strip(),None
    return m.group(1), (int(m.group(2)) if m.group(2) is not None else None)

def next_candidate_path(folder, stem, extension, source_path=None):
    wanted=_norm(stem);source=os.path.abspath(source_path) if source_path else None
    plain=False;used=set()
    try:names=os.listdir(folder)
    except OSError:names=[]
    for name in names:
        path=os.path.join(folder,name)
        if not os.path.isfile(path) or os.path.splitext(name)[1].lower()!=extension.lower():continue
        base,num=_candidate_base_and_number(os.path.splitext(name)[0])
        if _norm(base)!=wanted or (source and os.path.abspath(path)==source):continue
        if num is None:plain=True
        else:used.add(num)
    if not plain:return os.path.join(folder,stem+extension)
    n=1
    while n in used:n+=1
    return os.path.join(folder,"%s_%d%s"%(stem,n,extension))

def _suffix_family(folder, stem, extension):
    wanted=_norm(stem);items=[]
    try:names=os.listdir(folder)
    except OSError:return []
    for name in names:
        path=os.path.join(folder,name)
        if not os.path.isfile(path) or os.path.splitext(name)[1].lower()!=extension.lower():continue
        base,num=_candidate_base_and_number(os.path.splitext(name)[0])
        if _norm(base)==wanted:items.append((0 if num is None else num,name,path))
    return sorted(items,key=lambda x:(x[0],x[1].lower()))

def renumber_suffix_family(folder,stem,extension,dry_run=False,rename_callback=None):
    family=_suffix_family(folder,stem,extension);plan=[]
    for index,(_,name,path) in enumerate(family):
        target_name=stem+("" if index==0 else "_"+str(index))+extension
        if name!=target_name:plan.append((path,os.path.join(folder,target_name)))
    if dry_run or not plan:return plan
    staged=[];done=[]
    try:
        for source,target in plan:
            temp=os.path.join(folder,".renumber-"+next(tempfile._get_candidate_names())+extension)
            os.rename(source,temp);staged.append((source,temp,target))
        for source,temp,target in staged:
            if os.path.exists(target):raise FileExistsError(target)
            os.rename(temp,target);done.append((source,target))
            if rename_callback:rename_callback(source,target)
        return done
    except Exception:
        for source,target in reversed(done):
            if os.path.exists(target) and not os.path.exists(source):os.rename(target,source)
        for source,temp,target in reversed(staged):
            if os.path.exists(temp) and not os.path.exists(source):os.rename(temp,source)
        raise

def renumber_folder(folder,say=lambda message:None,dry_run=False,rename_callback=None):
    try:names=os.listdir(folder)
    except OSError:return []
    groups={}
    for name in names:
        if name.startswith('.'):continue
        ext=os.path.splitext(name)[1].lower();base,num=_candidate_base_and_number(os.path.splitext(name)[0])
        if ext=='.xlsx' and _norm(base)=='summary' and (num is not None or os.path.exists(os.path.join(folder,'Summary.xlsx'))):groups[('summary',ext)]=('Summary',ext)
        elif ext=='.pdf' and num is not None and 2<=len(base.split())<=4 and not (set(re.findall(r'[a-z]+',base.lower())) & {'jd','summary','resume','cv'}):groups[(_norm(base),ext)]=(base,ext)
    changed=[]
    for stem,ext in groups.values():
        plan=renumber_suffix_family(folder,stem,ext,dry_run=True)
        if plan:
            changed.extend(plan)
            if not dry_run:
                done=renumber_suffix_family(folder,stem,ext,rename_callback=rename_callback)
                for old,new in done:say("renumbered: %s -> %s"%(os.path.basename(old),os.path.basename(new)))
    return changed

def _next_summary_output(stage):
    return next_collision_path(stage, "Summary", ".xlsx")


def _summary_path(position_folder):
    stage = os.path.join(position_folder, "Ready for Manager Review")
    if not os.path.isdir(stage):
        return None, None
    canonical = os.path.join(stage, "Summary.xlsx")
    if os.path.isfile(canonical):
        return canonical, None
    choices = sorted((os.path.join(stage, n) for n in os.listdir(stage)
                      if re.fullmatch(r"Summary(?:_\d+)?\.xlsx", n, re.I)),
                     key=lambda p: (-os.path.getmtime(p), os.path.basename(p).lower() != "summary.xlsx"))
    if choices:
        return choices[0], None
    for name in os.listdir(position_folder):
        p = os.path.join(position_folder, name)
        if os.path.isfile(p) and re.fullmatch(r"Summary(?:_\d+)?\.xlsx", name, re.I):
            return canonical, p
    return None, None


def _update_tagged_cv_unlocked(pdf_path, tags=None, today=None):
    """Append/update one eligible CV in its existing stage summary; never move or alter the CV."""
    pdf_path = os.path.abspath(pdf_path)
    if tags is None:
        try:
            import butler
            tags = butler._tags_of_fast(pdf_path) or butler.get_tags(pdf_path)
        except Exception:
            tags = []
    if not eligible_pdf(pdf_path, tags):
        return {"status": "skipped", "reason": "not_a_ready_tagged_cv"}
    annotation, error = extract_sunsoft_fields(pdf_path)
    if error:
        return {"status": "skipped", "reason": error}
    fields = _candidate_fields(pdf_path, annotation)
    position = os.path.dirname(os.path.dirname(pdf_path))
    summary_path, template_path = _summary_path(position)
    if not summary_path:
        return {"status": "skipped", "reason": "no_client_summary_template_in_stage_or_position"}
    try:
        import openpyxl
        wb = openpyxl.load_workbook(template_path or summary_path)
    except Exception as exc:
        return {"status": "error", "reason": "summary_template_unreadable: " + str(exc)}
    ws = wb.active
    header_row, headers = _headers(ws)
    if not header_row:
        wb.close()
        return {"status": "error", "reason": "candidate_name_header_missing"}
    columns = _map_columns(headers)
    if "candidate name" not in columns:
        wb.close()
        return {"status": "error", "reason": "candidate_name_column_unmapped"}
    row = _candidate_row(ws, header_row, columns["candidate name"], fields["candidate name"])
    updated = row is not None
    if row is None:
        row = max(header_row + 1, ws.max_row + 1)
        if row > header_row + 1:
            for col in range(1, len(headers) + 1):
                src = ws.cell(row - 1, col)
                dst = ws.cell(row, col)
                if src.has_style:
                    dst._style = src._style
                if src.number_format:
                    dst.number_format = src.number_format
    if today is None:
        today = dt.date.today()
    values = dict(fields)
    values["date"] = dt.datetime.combine(today, dt.time.min)
    values["position"] = os.path.basename(position)
    if columns.get("s no"):
        values["s no"] = row - header_row
    written = []
    for key, col in columns.items():
        value = values.get(key)
        if value is None or (updated and key == "date" and ws.cell(row, col).value is not None):
            continue
        ws.cell(row, col).value = value
        written.append(key)
    fd, temp = tempfile.mkstemp(prefix=".summary-update-", suffix=".xlsx", dir=os.path.dirname(summary_path))
    os.close(fd)
    try:
        wb.save(temp)
        wb.close()
        backup_path = summary_path + ".pre-auto.bak"
        if os.path.exists(summary_path) and not os.path.exists(backup_path):
            shutil.copy2(summary_path, backup_path)
        if template_path and not os.path.exists(summary_path):
            shutil.copy2(template_path, summary_path)
        os.replace(temp, summary_path)
    except Exception as exc:
        try:
            wb.close()
        except Exception:
            pass
        try:
            os.unlink(temp)
        except OSError:
            pass
        return {"status": "error", "reason": "summary_save_failed: " + str(exc)}
    return {"status": "updated" if updated else "added", "candidate": fields["candidate name"],
            "summary": summary_path, "row": row, "fields_written": written,
            "fields_missing": [x for x in ("total experience", "current ctc", "expected ctc", "present location", "permanent location", "notice period") if x not in fields]}


def update_tagged_cv(pdf_path, tags=None, today=None):
    """Serialize summary upserts so concurrent watcher events cannot lose workbook rows."""
    with SUMMARY_LOCK:
        return _update_tagged_cv_unlocked(pdf_path, tags=tags, today=today)


def _selftest():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory(prefix='duplicate-name-test-') as d:
        Path(d,'Sandeep S Naik.pdf').write_bytes(b'first')
        Path(d,'Sandeep S. Naik.pdf').write_bytes(b'second')
        assert os.path.basename(next_candidate_path(d,'Sandeep S Naik','.pdf'))=='Sandeep S Naik_1.pdf'
        Path(d,'Sandeep S Naik_2.pdf').write_bytes(b'third')
        assert renumber_folder(d,dry_run=True)
        renumber_folder(d)
        assert sorted(p.name for p in Path(d).glob('*.pdf'))==['Sandeep S Naik.pdf','Sandeep S Naik_1.pdf','Sandeep S Naik_2.pdf']

    with tempfile.TemporaryDirectory(prefix='suffix-gap-test-') as d:
        for name in ('Sandeep S Naik.pdf','Sandeep S Naik_2.pdf','Summary.xlsx','Summary_2.xlsx'):
            with open(os.path.join(d,name),'wb') as f:f.write(name.encode())
        changes=renumber_folder(d,dry_run=True)
        assert len(changes)==2,changes
        renumber_folder(d)
        assert sorted(os.listdir(d))==['Sandeep S Naik.pdf','Sandeep S Naik_1.pdf','Summary.xlsx','Summary_1.xlsx']

    source_root = "/Users/apple/Downloads/Sunsoft Technology"
    cv = os.path.join(source_root, "02 Honda Power", "Engineer-Machining_(Steel_Shop)_-Greater_Noida_Location", "Ready for Manager Review", "Lalan Kumar.pdf")
    template = os.path.join(source_root, "02 Honda Power", "Engineer-Machining_(Steel_Shop)_-Greater_Noida_Location", "Ready for Manager Review", "Summary.xlsx")
    if not (os.path.isfile(cv) and os.path.isfile(template)):
        print("summary_builder selftest: SKIP (local sample CV/template unavailable)")
        return
    import hashlib
    before_cv = hashlib.sha256(open(cv, "rb").read()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="summary-builder-test-") as root:
        pos = Path(root) / "01 Client" / "Role A"
        stage = pos / "Ready for Manager Review"
        stage.mkdir(parents=True)
        temp_cv = stage / "Lalan Kumar.pdf"
        shutil.copy2(cv, temp_cv)
        out = stage / "Summary.xlsx"
        shutil.copy2(template, out)
        result = update_tagged_cv(str(temp_cv), tags=["Ready for Manager Review"], today=dt.date(2026, 11, 11))
        assert result["status"] in ("added", "updated"), result
        import openpyxl
        wb = openpyxl.load_workbook(out, data_only=True)
        ws = wb.active
        hdr_row, headers = _headers(ws)
        cols = _map_columns(headers)
        row = _candidate_row(ws, hdr_row, cols["candidate name"], "Lalan Kumar")
        assert row is not None
        assert ws.cell(row, cols["total experience"]).value == "3.7 years"
        assert ws.cell(row, cols["current ctc"]).value == "5.5 LPA"
        assert ws.cell(row, cols["expected ctc"]).value == "7 LPA"
        assert ws.cell(row, cols["notice period"]).value == "30 days"
        original_date = ws.cell(row, cols["date"]).value if "date" in cols else None
        wb.close()
        repeated = update_tagged_cv(str(temp_cv), tags=["Ready for Manager Review"], today=dt.date(2026, 11, 12))
        assert repeated["status"] == "updated" and repeated["row"] == row
        wb = openpyxl.load_workbook(out, data_only=True)
        ws = wb.active
        assert _candidate_row(ws, hdr_row, cols["candidate name"], "Lalan Kumar") == row
        if original_date is not None and "date" in cols:
            assert ws.cell(row, cols["date"]).value == original_date
        wb.close()
        skipped = update_tagged_cv(str(temp_cv), tags=[], today=dt.date(2026, 11, 11))
        assert skipped["status"] == "skipped"
        wb = openpyxl.load_workbook(out, data_only=True)
        ws = wb.active
        assert _candidate_row(ws, hdr_row, cols["candidate name"], "Lalan Kumar") is not None
        wb.close()
        second_cv = stage / "Lalan Kumar_1.pdf"
        shutil.copy2(cv, second_cv)
        batch_out = stage / "Summary_1.xlsx"
        batch = build_selected_summary([str(temp_cv), str(second_cv)], str(out), output_path=str(batch_out), tags_by_path={str(temp_cv):["Ready for Manager Review"], str(second_cv):["Ready for Manager Review"]}, today=dt.date(2026,11,11))
        assert batch['status']=='created' and batch['count']==2, batch
        bw=openpyxl.load_workbook(batch_out,data_only=True); bs=bw.active
        br, bh=_headers(bs); bc=_map_columns(bh)
        assert _candidate_row(bs,br,bc['candidate name'],'Lalan Kumar') is not None
        assert _candidate_row(bs,br,bc['candidate name'],'Lalan Kumar_1') is not None
        bw.close()
        named_out=stage/'Summary_2.xlsx'
        named=build_selected_summary([str(temp_cv),str(second_cv)],str(out),output_path=str(named_out),base_names={str(temp_cv):'Sandeep S. Naik',str(second_cv):'Sandeep S Naik'},tags_by_path={str(temp_cv):['Ready for Manager Review'],str(second_cv):['Ready for Manager Review']},today=dt.date(2026,11,11))
        assert named['status']=='created' and named['count']==2
        nw=openpyxl.load_workbook(named_out,data_only=True);ns=nw.active;nr,nh=_headers(ns);nc=_map_columns(nh)
        assert _candidate_row(ns,nr,nc['candidate name'],'Sandeep S. Naik') is not None
        assert _candidate_row(ns,nr,nc['candidate name'],'Sandeep S Naik') is not None
        nw.close()
        with tempfile.TemporaryDirectory(prefix='summary-suffix-test-') as suffix_dir:
            for basename in ('Sandeep S Naik.pdf','Sandeep S Naik_2.pdf','Summary.xlsx','Summary_2.xlsx'):
                (Path(suffix_dir)/basename).write_bytes(basename.encode())
            renumber_folder(suffix_dir)
            assert sorted(x.name for x in Path(suffix_dir).glob('Sandeep*.pdf')) == ['Sandeep S Naik.pdf','Sandeep S Naik_1.pdf']
            assert sorted(x.name for x in Path(suffix_dir).glob('Summary*.xlsx')) == ['Summary.xlsx','Summary_1.xlsx']
    assert hashlib.sha256(open(cv, "rb").read()).hexdigest() == before_cv
    print("summary_builder selftest: PASS (tag gate, annotation fields, template, CV unchanged)")


def _summary_template_for(paths):  # SUMMARY-RESOLVE v85.142: ctrl+s finds its client's canonical workbook in silence; the chooser survives only as fallback for orphans
    try:
        import json as _sj, os as _so, re as _sr
        _cl = _sj.load(open(_so.path.join(_so.path.dirname(_so.path.abspath(__file__)), 'clients.json')))
        for _p in paths:
            _parts = _p.replace('\\', '/').split('/')
            for _i, _c in enumerate(_parts):
                if _sr.match(r'^\d{2} ', _c) and _sr.sub(r'^\d+ ', '', _c).strip().lower().replace(' ', '') in {v.lower().replace(' ', '') for v in _cl.values()}:
                    _root = '/'.join(_parts[:_i])
                    _cand = _root + '/99 Summary/' + _c + ' Summary.xlsx'
                    if _so.path.exists(_cand):
                        return _cand
        return ''
    except Exception:
        return ''

def _summary_template_for(paths):  # SUMMARY-RESOLVE v85.142: ctrl+s finds its client's canonical workbook in silence; the chooser survives only as fallback for orphans
    try:
        import json as _sj, os as _so, re as _sr
        _cl = _sj.load(open(_so.path.join(_so.path.dirname(_so.path.abspath(__file__)), 'clients.json')))
        for _p in paths:
            _parts = _p.replace('\\', '/').split('/')
            for _i, _c in enumerate(_parts):
                if _sr.match(r'^\d{2} ', _c) and _sr.sub(r'^\d+ ', '', _c).strip().lower().replace(' ', '') in {v.lower().replace(' ', '') for v in _cl.values()}:
                    _root = '/'.join(_parts[:_i])
                    _cand = _root + '/99 Summary/' + _c + ' Summary.xlsx'
                    if _so.path.exists(_cand):
                        return _cand
        return ''
    except Exception:
        return ''

def _run_summary_maker_cli(paths, template=None):
    selected=[os.path.abspath(os.path.expanduser(p)) for p in paths if p.lower().endswith('.pdf')]
    if not selected: raise SystemExit('Select one or more CV PDF files in Finder.')
    if len({os.path.dirname(p) for p in selected})!=1: raise SystemExit('Select CVs from one folder.')
    stage=os.path.dirname(selected[0])
    if os.path.basename(stage).strip().lower()!=READY_FOLDER: raise SystemExit('Selected CVs must be in Ready for Manager Review.')
    if not template:
        if not template:
            template = _summary_template_for(selected) or None
            if template: print('summary template: %s' % template)  # SUMMARY-RESOLVE v85.142: the resolver names its winner aloud
        if not template: print('summary template: chooser fallback - no client chair matched')  # SUMMARY-RESOLVE v85.142
        if not template:
            template = _summary_template_for(selected) or None
            if template: print('summary template: %s' % template)  # SUMMARY-RESOLVE v85.142: the resolver names its winner aloud
        if not template: print('summary template: chooser fallback - no client chair matched')  # SUMMARY-RESOLVE v85.142
        import subprocess
        chooser='POSIX path of (choose file with prompt "Choose this client\'s existing Summary workbook" of type {"org.openxmlformats.spreadsheetml.sheet"})'
        result=subprocess.run(['osascript','-e',chooser],capture_output=True,text=True)
        template=(result.stdout or '').strip() if result.returncode==0 else None
    if not template: raise SystemExit('No client template chosen; nothing was created.')
    result=build_selected_summary(selected,template,say=print,base_names={p:os.path.splitext(os.path.basename(p))[0] for p in selected})
    if result.get('status')!='created': raise SystemExit(result.get('reason','Summary Maker failed.'))
    print('Created:',result['summary'],'· candidates:',result['count'])

if __name__ == "__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='--selected':
        args=sys.argv[2:]; template=None
        if '--template' in args:
            i=args.index('--template'); template=args[i+1]; args=args[:i]+args[i+2:]
        _run_summary_maker_cli(args,template)
    else:
        _selftest()

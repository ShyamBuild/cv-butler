"""Read-only recruiting desk built from the existing Sunsoft folder stages."""
import argparse
import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path

INTAKE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "role_intake.json")
STAGES = {
    "ready for manager review": "Ready for Manager Review",
    "feedback pending": "Feedback Pending",
    "interview scheduled": "Interview Scheduled",
    "interview today": "Interview Today",
    "interview tomorrow": "Interview Tomorrow",
    "call scheduled": "Call Scheduled",
    "awaiting cv update": "Awaiting CV Update",
    "awaiting jd confirmation": "Awaiting JD Confirmation",
    "interview cleared": "Interview Cleared",
    "expected to join": "Expected to Join",
    "joined - payment pending": "Joined - Payment Pending",
    "joined – payment pending": "Joined – Payment Pending",
    "payment received": "Payment Received",
    "rejected by client": "Rejected by Client",
    "closed – not proceeding": "Closed – Not Proceeding",
    "closed - not proceeding": "Closed - Not Proceeding",
}
SKIP_DIRS = {
    "archive", "patches", "logs", "backups", "converted files",
    "converted doc files", "duplicates", "previous versions", "ta_output",
    "untitled folder", "untitled folder 2", "ready for manager review",
    "feedback pending", "interview scheduled", "interview today",
    "interview tomorrow", "call scheduled", "awaiting cv update",
    "awaiting jd confirmation", "interview cleared", "expected to join",
    "joined - payment pending", "joined – payment pending",
    "payment received", "rejected by client", "closed – not proceeding",
    "closed - not proceeding",
}
STAGE_PRIORITY = (
    "Interview Today", "Interview Tomorrow", "Interview Scheduled",
    "Ready for Manager Review", "Feedback Pending", "Call Scheduled",
    "Awaiting CV Update", "Awaiting JD Confirmation", "Interview Cleared",
    "Expected to Join", "Joined - Payment Pending", "Payment Received",
)


def _workspace_root(root):
    current = os.path.abspath(os.path.expanduser(str(root)))
    while os.path.isdir(current):
        try:
            names = os.listdir(current)
        except OSError:
            names = []
        numbered = [name for name in names
                    if os.path.isdir(os.path.join(current, name))
                    and __import__("re").match(r"^\d{2}\s", name)]
        if len(numbered) >= 3 and os.path.isfile(os.path.join(current, "stage_log.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(os.path.expanduser(str(root)))


def _load_intakes(path=INTAKE_FILE):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError, TypeError):
        return []


def _save_intakes(rows, path=INTAKE_FILE):
    parent = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".role-intake-", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _parse_due_date(text, today=None):
    value = (text or "").strip().lower()
    if not value:
        return None
    base = today or dt.date.today()
    if value in ("today", "eod", "today eod", "4pm", "5pm", "4-5pm"):
        return base.isoformat()
    if value == "tomorrow":
        return (base + dt.timedelta(days=1)).isoformat()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"):
        try:
            return dt.datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Use today, tomorrow, or a date like 2026-11-12.")


def create_intake(client, role, location, must_haves, deal_breakers, due, notes="", source="manager call", path=INTAKE_FILE, today=None, now=None):
    client = (client or "").strip()
    role = (role or "").strip()
    if not client or not role:
        raise ValueError("Client and role are required.")
    due_date = _parse_due_date(due, today=today)
    now = now or dt.datetime.now()
    record = {
        "id": now.strftime("%Y%m%d-%H%M%S"),
        "client": client,
        "role": role,
        "location": (location or "").strip(),
        "must_haves": [x.strip() for x in re.split(r"[,;\n]", must_haves or "") if x.strip()],
        "deal_breakers": [x.strip() for x in re.split(r"[,;\n]", deal_breakers or "") if x.strip()],
        "first_lot_due": due_date,
        "status": "intake",
        "source": (source or "manager call").strip(),
        "notes": (notes or "").strip(),
        "opened_at": now.isoformat(timespec="seconds"),
    }
    rows = _load_intakes(path)
    duplicate = next((row for row in rows if row.get("status") == "intake" and row.get("client", "").casefold() == client.casefold() and row.get("role", "").casefold() == role.casefold()), None)
    if duplicate:
        raise ValueError("An intake for this client and role is already open (" + duplicate.get("id", "existing") + ").")
    rows.append(record)
    _save_intakes(rows, path)
    return record


def guided_intake(input_fn=input, say=print, path=INTAKE_FILE, today=None, now=None):
    say("🆕 NEW ROLE INTAKE · no folders or candidate files will be changed")
    prompts = (
        ("Client", True), ("Role title", True), ("Job location", False),
        ("Must-have skills / experience (comma-separated)", False),
        ("Deal-breakers (comma-separated)", False),
        ("First candidate lot due (today / tomorrow / date)", True),
        ("Manager notes / ResDex search reference", False),
    )
    answers = []
    for label, required in prompts:
        while True:
            value = input_fn(label + ": ").strip()
            if required and not value:
                say("Please enter " + label.lower() + ".")
                continue
            answers.append(value)
            break
    record = create_intake(answers[0], answers[1], answers[2], answers[3], answers[4], answers[5], answers[6], path=path, today=today, now=now)
    say("✅ intake saved · " + record["client"] + " / " + record["role"] + " · first lot due " + record["first_lot_due"])
    return record


def intake_summary(rows=None, today=None):
    day = today or dt.date.today()
    rows = _load_intakes() if rows is None else rows
    active = [r for r in rows if r.get("status") == "intake"]
    active.sort(key=lambda r: (r.get("first_lot_due") or "9999-99-99", r.get("opened_at", "")))
    return {"active": len(active), "due_today": sum(r.get("first_lot_due") == day.isoformat() for r in active), "rows": active}


def _is_candidate_pdf(name):
    low = os.path.splitext(name)[0].strip().lower()
    return (name.lower().endswith(".pdf")
            and not low.startswith(("jd", "_jd", "summary", "resdex report"))
            and not low.endswith((" jd", "- jd", "_jd"))
            and " job description" not in low)


def _candidate_pdfs(folder):
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return []
    return [name for name in names if _is_candidate_pdf(name)]


def _role_snapshot(position):
    counts = {}
    samples = {}
    newest = 0.0
    has_jd = False
    try:
        entries = sorted(os.listdir(position))
    except OSError:
        return None
    for name in entries:
        path = os.path.join(position, name)
        if os.path.isfile(path) and name.lower().endswith(".pdf") and name.lower().startswith(("jd", "_jd")):
            has_jd = True
            try:
                newest = max(newest, os.path.getmtime(path))
            except OSError:
                pass
        if not os.path.isdir(path):
            continue
        canonical = STAGES.get(name.strip().lower())
        if not canonical:
            continue
        candidates = _candidate_pdfs(path)
        if candidates:
            counts[canonical] = counts.get(canonical, 0) + len(candidates)
            samples.setdefault(canonical, []).extend(candidates[:3])
            for candidate in candidates:
                try:
                    newest = max(newest, os.path.getmtime(os.path.join(path, candidate)))
                except OSError:
                    pass
    root_candidates = _candidate_pdfs(position)
    if root_candidates:
        counts["Unstaged"] = len(root_candidates)
        samples["Unstaged"] = root_candidates[:3]
        for candidate in root_candidates:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(position, candidate)))
            except OSError:
                pass
    if not (has_jd or counts):
        return None
    return {"path": position, "counts": counts, "samples": samples,
            "has_jd": has_jd, "newest": newest}


def _priority(role):
    counts = role["counts"]
    return next((i for i, stage in enumerate(STAGE_PRIORITY) if counts.get(stage)),
                len(STAGE_PRIORITY) if counts.get("Unstaged") else len(STAGE_PRIORITY) + 1)


def build_desk(root, today=None):
    """Return recruiting priorities without writing to the workspace."""
    base = _workspace_root(root)
    day = today or dt.date.today()
    roles = []
    try:
        clients = sorted(os.listdir(base))
    except OSError:
        return {"today": day.isoformat(), "roles": [], "error": "workspace is unavailable"}
    for client in clients:
        client_path = os.path.join(base, client)
        if client.startswith(".") or client.lower() in SKIP_DIRS or not os.path.isdir(client_path):
            continue
        try:
            position_names = sorted(os.listdir(client_path))
        except OSError:
            continue
        for title in position_names:
            position = os.path.join(client_path, title)
            low = title.strip().lower()
            if (title.startswith(".") or low in SKIP_DIRS or low.startswith(("jd", "fw", "untitled"))
                    or not os.path.isdir(position)):
                continue
            snapshot = _role_snapshot(position)
            if snapshot:
                snapshot.update({"client": client, "title": title})
                roles.append(snapshot)
    roles.sort(key=lambda role: (_priority(role), -role["newest"], role["client"].lower(), role["title"].lower()))
    return {"today": day.isoformat(), "roles": roles}


def render_desk(desk, say=print):
    say("🌅 RECRUITING DESK · " + desk["today"])
    if desk.get("error"):
        say("⚠️ " + desk["error"])
        return
    roles = desk["roles"]
    intake = intake_summary(today=dt.date.fromisoformat(desk["today"]))
    if not roles:
        say("No roles with a JD or candidate CVs found in this workspace yet.")
        if intake["active"]:
            say("Active role intakes: " + str(intake["active"]) + " · due today: " + str(intake["due_today"]))
            for row in intake["rows"][:5]:
                say("   • " + row["client"] + " / " + row["role"] + " · first lot " + (row.get("first_lot_due") or "date unset"))
        return
    say("Priority order: scheduled interviews, manager-ready CVs, feedback, then candidate follow-ups.")
    say("Same-day target: move quality candidates toward manager submission by 4–5 PM.")
    if intake["active"]:
        say("\n🆕 Active role intakes: " + str(intake["active"]) + " · due today: " + str(intake["due_today"]))
        for row in intake["rows"][:5]:
            say("   • " + row["client"] + " / " + row["role"] + " · first lot " + (row.get("first_lot_due") or "date unset"))
    for role in roles[:12]:
        counts = role["counts"]
        total = sum(counts.values())
        say("\n📌 " + role["client"] + " / " + role["title"])
        say("   CVs in tracked stages: " + str(total) + (" · JD found" if role["has_jd"] else " · JD not found at position root"))
        active = [(stage, counts[stage]) for stage in STAGE_PRIORITY if counts.get(stage)]
        if counts.get("Unstaged"):
            active.append(("Unstaged", counts["Unstaged"]))
        for stage, count in active[:4]:
            say("   " + str(count) + " · " + stage)
            for name in role["samples"].get(stage, [])[:2]:
                say("      - " + os.path.splitext(name)[0])
        first = next((stage for stage in STAGE_PRIORITY if counts.get(stage)), None)
        if first == "Interview Today":
            action = "confirm candidate and interview logistics"
        elif first in ("Interview Tomorrow", "Interview Scheduled"):
            action = "confirm interview details and prepare candidate"
        elif counts.get("Ready for Manager Review"):
            action = "send the manager-ready lot before today's cutoff"
        elif counts.get("Feedback Pending"):
            action = "follow up with the manager for feedback"
        elif counts.get("Call Scheduled"):
            action = "call candidates and record interest"
        elif counts.get("Awaiting CV Update"):
            action = "follow up for the updated CV"
        elif counts.get("Awaiting JD Confirmation"):
            action = "confirm JD acknowledgement"
        elif counts.get("Unstaged"):
            action = "review and stage the downloaded CVs"
        elif role["has_jd"]:
            action = "start quality sourcing for this open role"
        else:
            action = "review current role activity"
        say("   ➜ Next: " + action)
    if len(roles) > 12:
        say("\n… plus " + str(len(roles) - 12) + " more roles. Use the position folders to narrow the desk.")
    say("\nRead-only: no CVs moved, edited, downloaded, or sent.")


def run(root, say=print, today=None):
    desk = build_desk(root, today=today)
    render_desk(desk, say)
    return desk


def _selftest():
    import tempfile
    with tempfile.TemporaryDirectory(prefix="recruit-desk-test-") as root:
        position = Path(root) / "01 Client" / "Role A"
        (position / "Ready for Manager Review").mkdir(parents=True)
        (position / "Interview Today").mkdir()
        (position / "Feedback Pending").mkdir()
        (position / "Ready for Manager Review" / "Candidate One.pdf").write_bytes(b"fixture")
        (position / "Interview Today" / "Candidate Two.pdf").write_bytes(b"fixture")
        (position / "Feedback Pending" / "Candidate Three.pdf").write_bytes(b"fixture")
        (position / "JD Role.pdf").write_bytes(b"JD fixture")
        (position / "Ready for Manager Review" / "Summary.xlsx").write_bytes(b"summary fixture")
        for client in ("02 Client", "03 Client"):
            (Path(root) / client).mkdir()
        (Path(root) / "stage_log.json").write_text("{}")
        (position / "Fleet Supervisor - SBI - JD.pdf").write_bytes(b"JD duplicate fixture")
        before = {str(p.relative_to(root)): p.read_bytes() for p in Path(root).rglob("*") if p.is_file()}
        assert _workspace_root(str(position)) == root
        desk = build_desk(str(position), today=dt.date(2026, 11, 11))
        assert len(desk["roles"]) == 1
        role = desk["roles"][0]
        assert role["counts"] == {"Interview Today": 1, "Feedback Pending": 1, "Ready for Manager Review": 1}
        assert _priority(role) == 0
        after = {str(p.relative_to(root)): p.read_bytes() for p in Path(root).rglob("*") if p.is_file()}
        assert before == after
        intake_path = str(Path(root) / "role_intake.json")
        created = create_intake("02 HIPP", "Quality Engineer", "Greater Noida", "CNC, quality", "night shift", "today", "called by manager", path=intake_path, today=dt.date(2026, 11, 11), now=dt.datetime(2026, 11, 11, 9, 30))
        assert created["first_lot_due"] == "2026-11-11" and created["must_haves"] == ["CNC", "quality"]
        summary = intake_summary(_load_intakes(intake_path), dt.date(2026, 11, 11))
        assert summary["active"] == 1 and summary["due_today"] == 1
        try:
            create_intake("02 HIPP", "Quality Engineer", "", "", "", "today", path=intake_path)
        except ValueError:
            pass
        else:
            raise AssertionError("duplicate open intake accepted")
        try:
            create_intake("02 HIPP", "Other Role", "", "", "", "not-a-date", path=intake_path)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid deadline accepted")
        assert all((Path(root) / name).exists() for name in ["01 Client", "02 Client", "03 Client", "stage_log.json"])
        assert (Path(root) / "role_intake.json").is_file()
        after_with_intake = {str(p.relative_to(root)): p.read_bytes() for p in Path(root).rglob("*") if p.is_file() and p.name != "role_intake.json"}
        assert before == after_with_intake
        lines = []
        render_desk(desk, lines.append)
        text = "\n".join(lines)
        assert "Candidate Two" in text and "confirm candidate and interview logistics" in text
        assert "Summary" not in text and "JD Role" not in text and "Fleet Supervisor" not in text
    print("recruit.py selftest: PASS (priority, counts, exclusions, read-only)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read-only Sunsoft recruiting priority desk")
    parser.add_argument("--root", default="~/Downloads/Sunsoft Technology")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--new-role", action="store_true", help="start the guided new-role intake")
    args = parser.parse_args()
    if args.selftest:
        _selftest()
    elif args.new_role:
        guided_intake()
    else:
        run(args.root)

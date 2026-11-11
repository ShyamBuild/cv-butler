"""Read-only recruiting desk built from the existing Sunsoft folder stages."""
import argparse
import datetime as dt
import os
from pathlib import Path

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
    if not roles:
        say("No roles with a JD or candidate CVs found in this workspace yet.")
        return
    say("Priority order: scheduled interviews, manager-ready CVs, feedback, then candidate follow-ups.")
    say("Same-day target: move quality candidates toward manager submission by 4–5 PM.")
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
    args = parser.parse_args()
    if args.selftest:
        _selftest()
    else:
        run(args.root)

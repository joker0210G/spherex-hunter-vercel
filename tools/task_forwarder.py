#!/usr/bin/env python3
"""
🚀 Team RIP: Teammate Task Dispatcher & Compute/Token Forwarder
NASA Space Apps Challenge 2026 - Planet X & SPHEREx
Allows teammates with asymmetrical resources (laptop specs / token quotas)
to forward, claim, execute, and deliver tasks seamlessly via Git.
"""

import argparse
import datetime
import os
import re
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SYNC_DIR = os.path.join(BASE_DIR, "07 - Team Memory & Sync", "TASK_DISPATCH")
INBOX_DIR = os.path.join(SYNC_DIR, "inbox")
COMPLETED_DIR = os.path.join(SYNC_DIR, "completed")
BOARD_FILE = os.path.join(SYNC_DIR, "TASK_FORWARDING_BOARD.md")

TEAM_MEMBERS = ["jokerodu", "darkodu", "coolodu", "iceodu", "astrodu"]

def ensure_dirs():
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(COMPLETED_DIR, exist_ok=True)

def parse_frontmatter(content):
    meta = {}
    body = content
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        for line in fm_text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body

def dump_frontmatter(meta, body):
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    return "\n".join(lines)

def get_next_task_id():
    ensure_dirs()
    existing_ids = []
    for d in [INBOX_DIR, COMPLETED_DIR]:
        if not os.path.exists(d): continue
        for f in os.listdir(d):
            m = re.match(r"^TASK-(\d+)", f)
            if m:
                existing_ids.append(int(m.group(1)))
    next_num = max(existing_ids, default=0) + 1
    return f"TASK-{next_num:03d}"

def update_board():
    ensure_dirs()
    tasks = []

    # Read inbox tasks
    for f in sorted(os.listdir(INBOX_DIR)):
        if not f.endswith(".md"): continue
        path = os.path.join(INBOX_DIR, f)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                meta, _ = parse_frontmatter(fp.read())
                meta["filename"] = f
                meta["location"] = "inbox"
                tasks.append(meta)
        except Exception: pass

    # Read completed tasks
    for f in sorted(os.listdir(COMPLETED_DIR), reverse=True):
        if not f.endswith(".md"): continue
        path = os.path.join(COMPLETED_DIR, f)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                meta, _ = parse_frontmatter(fp.read())
                meta["filename"] = f
                meta["location"] = "completed"
                tasks.append(meta)
        except Exception: pass

    # Build Markdown table
    rows = []
    for t in tasks:
        t_id = t.get("task_id", "UNKNOWN")
        t_title = t.get("title", "Untitled")
        t_from = t.get("requested_by", "-")
        t_to = t.get("assigned_to", "-")
        t_type = t.get("type", "normal")
        t_prio = t.get("priority", "NORMAL")
        t_status = t.get("status", "PENDING")
        t_out = t.get("output_path", t.get("source_branch", "-"))

        status_emoji = "🟡" if t_status == "PENDING" else ("🔵" if t_status == "CLAIMED" else "🟢")
        rows.append(f"| **{t_id}** | {t_title} | `@{t_from}` | `@{t_to}` | `{t_type}` | `{t_prio}` | {status_emoji} {t_status} | `{t_out}` |")

    if not rows:
        table_content = "| *No active tasks* | *Queue is currently clear* | - | - | - | - | 🟢 Idle | - |"
    else:
        table_content = "\n".join(rows)

    board_text = f"""# 📋 Team RIP: Master Task Forwarding Board
> **Live Task Forwarding Ledger** | Synced via Git across all branches
> **Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Active Tasks:** {len([t for t in tasks if t.get('status') != 'COMPLETED'])}

---

## 🚦 Live Task Dispatch Status

| Task ID | Title | Requester | Assigned Worker | Type | Priority | Status | Branch / Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_content}

---

## 📥 Quick Commands

- **Forward a task:** `python tools/task_forwarder.py dispatch --from <name> --to <name> --type <token_heavy|compute_heavy> --title "..." --brief "..."`
- **Check assigned tasks:** `python tools/task_forwarder.py check --worker <name>`
- **View task board:** `python tools/task_forwarder.py list`
- **Claim a task:** `python tools/task_forwarder.py claim --task <TASK-ID> --worker <name>`
- **Complete a task:** `python tools/task_forwarder.py complete --task <TASK-ID> --output "<path>"`
"""
    try:
        with open(BOARD_FILE, "w", encoding="utf-8") as fp:
            fp.write(board_text)
    except Exception as e:
        print(f"Warning: Could not update board file: {e}")

def cmd_dispatch(args):
    ensure_dirs()
    task_id = get_next_task_id()
    now_str = datetime.datetime.now().isoformat()

    meta = {
        "task_id": task_id,
        "title": args.title,
        "requested_by": args.requester,
        "assigned_to": args.to,
        "type": args.type,
        "priority": args.priority.upper(),
        "status": "PENDING",
        "created_at": now_str,
        "source_branch": args.branch or "main"
    }

    body = f"""# Task: {args.title}
> **Requester:** @{args.requester} | **Assigned To:** @{args.to}
> **Resource Type:** `{args.type}` | **Priority:** `{args.priority}`

## 📝 Objective & Brief:
{args.brief}

## 🎯 Definition of Done:
- [ ] Task executed by @{args.to} using optimal hardware/token capabilities.
- [ ] Output artifacts committed to branch `{meta['source_branch']}` or specified destination.
- [ ] Task marked as completed via `python tools/task_forwarder.py complete --task {task_id}`.
"""
    filename = f"{task_id}_{args.to}.md"
    filepath = os.path.join(INBOX_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as fp:
        fp.write(dump_frontmatter(meta, body))

    update_board()
    print(f"\n✅ [DISPATCHED] Task ticket created: {task_id}")
    print(f"   📄 File: {filepath}")
    print(f"   👤 From: @{args.requester} -> To: @{args.to}")
    print(f"   🏷️ Type: {args.type} | Priority: {args.priority}")
    print(f"\n📢 Next Step: Commit and push your branch to GitHub so @{args.to} can fetch it!")
    print(f"   git add \"07 - Team Memory & Sync/TASK_DISPATCH/inbox/{filename}\"")
    print(f"   git commit -m \"dispatch({task_id}): {args.title}\"")
    print(f"   git push origin {meta['source_branch']}\n")

def cmd_list(args):
    ensure_dirs()
    update_board()

    inbox_files = [f for f in os.listdir(INBOX_DIR) if f.endswith(".md")]
    completed_files = [f for f in os.listdir(COMPLETED_DIR) if f.endswith(".md")]

    print("\n" + "="*80)
    print("🛰️  TEAM RIP: ASYMMETRIC TASK FORWARDING & DELEGATION BOARD")
    print("="*80)

    if not inbox_files:
        print("\n🟢 INBOX: No pending tasks. Queue is clear!")
    else:
        print(f"\n📥 INBOX ({len(inbox_files)} active tickets):")
        for f in sorted(inbox_files):
            p = os.path.join(INBOX_DIR, f)
            with open(p, "r", encoding="utf-8") as fp:
                meta, _ = parse_frontmatter(fp.read())
                t_id = meta.get("task_id", f)
                t_to = meta.get("assigned_to", "all")
                t_from = meta.get("requested_by", "unknown")
                t_title = meta.get("title", "Untitled")
                t_status = meta.get("status", "PENDING")
                t_type = meta.get("type", "normal")
                print(f"  • [{t_id}] [{t_status}] {t_title}")
                print(f"      From: @{t_from} -> To: @{t_to} | Type: {t_type}")

    if completed_files:
        print(f"\n✅ COMPLETED ({len(completed_files)} archived tickets):")
        for f in sorted(completed_files, reverse=True)[:5]:
            p = os.path.join(COMPLETED_DIR, f)
            with open(p, "r", encoding="utf-8") as fp:
                meta, _ = parse_frontmatter(fp.read())
                t_id = meta.get("task_id", f)
                t_title = meta.get("title", "Untitled")
                print(f"  ✓ [{t_id}] {t_title} (Completed by @{meta.get('assigned_to')})")

    print("\n" + "="*80 + "\n")

def cmd_check(args):
    ensure_dirs()
    worker = args.worker.lower().strip()
    assigned = []

    for f in os.listdir(INBOX_DIR):
        if not f.endswith(".md"): continue
        p = os.path.join(INBOX_DIR, f)
        try:
            with open(p, "r", encoding="utf-8") as fp:
                meta, body = parse_frontmatter(fp.read())
                to_user = meta.get("assigned_to", "").lower().strip()
                status = meta.get("status", "PENDING")
                if (to_user == worker or to_user in ["all", "any"]) and status in ["PENDING", "CLAIMED"]:
                    assigned.append((meta, body, p))
        except Exception: pass

    if not assigned:
        print(f"🟢 [NO PENDING TASKS] No dispatched tasks waiting for @{worker}.")
        return

    print("\n" + "🔔"*35)
    print(f"📢 [TASK ALERT] @{worker}, you have {len(assigned)} pending task(s) assigned to you!")
    print("🔔"*35)
    for meta, body, _ in assigned:
        print(f"\n📌 [{meta.get('task_id')}] {meta.get('title')}")
        print(f"   From: @{meta.get('requested_by')} | Priority: {meta.get('priority')} | Type: {meta.get('type')}")
        print(f"   Status: {meta.get('status')}")
        print("   Brief Preview:")
        lines = [l for l in body.splitlines() if l.strip() and not l.startswith("#") and not l.startswith(">")]
        for l in lines[:3]:
            print(f"     {l}")
    print("\n💡 Run `python tools/task_forwarder.py claim --task <TASK_ID> --worker " + worker + "` to claim it!")
    print("="*70 + "\n")

def cmd_claim(args):
    ensure_dirs()
    task_id = args.task.upper().strip()
    worker = args.worker.lower().strip()

    target_file = None
    for f in os.listdir(INBOX_DIR):
        if f.startswith(task_id):
            target_file = os.path.join(INBOX_DIR, f)
            break

    if not target_file:
        print(f"❌ Error: Task {task_id} not found in inbox.")
        return

    with open(target_file, "r", encoding="utf-8") as fp:
        meta, body = parse_frontmatter(fp.read())

    meta["status"] = "CLAIMED"
    meta["claimed_by"] = worker
    meta["claimed_at"] = datetime.datetime.now().isoformat()

    with open(target_file, "w", encoding="utf-8") as fp:
        fp.write(dump_frontmatter(meta, body))

    update_board()
    print(f"🔵 [CLAIMED] Task {task_id} is now claimed by @{worker}.")
    print("   You can now execute this task with your high specs / tokens!")

def cmd_complete(args):
    ensure_dirs()
    task_id = args.task.upper().strip()

    target_file = None
    target_name = None
    for f in os.listdir(INBOX_DIR):
        if f.startswith(task_id):
            target_file = os.path.join(INBOX_DIR, f)
            target_name = f
            break

    if not target_file:
        print(f"❌ Error: Task {task_id} not found in inbox.")
        return

    with open(target_file, "r", encoding="utf-8") as fp:
        meta, body = parse_frontmatter(fp.read())

    meta["status"] = "COMPLETED"
    meta["completed_at"] = datetime.datetime.now().isoformat()
    if args.output:
        meta["output_path"] = args.output

    if args.notes:
        body += f"\n\n## 🏁 Completion Notes (@{meta.get('assigned_to')}):\n{args.notes}\nOutput delivered: `{args.output or 'See commit'}`\n"

    dest_file = os.path.join(COMPLETED_DIR, target_name)
    with open(dest_file, "w", encoding="utf-8") as fp:
        fp.write(dump_frontmatter(meta, body))

    os.remove(target_file)
    update_board()

    print(f"\n🎉 [COMPLETED] Task {task_id} finished successfully!")
    print(f"   Moved ticket to: {dest_file}")
    if args.output:
        print(f"   📦 Output artifact: {args.output}")
    print(f"\n📢 Next Step: Commit and push to Git so @{meta.get('requested_by')} receives your completed work!")

def main():
    parser = argparse.ArgumentParser(description="Team RIP Task Forwarder & Resource Balancer")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # dispatch
    p_disp = subparsers.add_parser("dispatch", help="Forward a task to a teammate")
    p_disp.add_argument("--from", dest="requester", required=True, help="Your username (e.g. iceodu)")
    p_disp.add_argument("--to", required=True, help="Target teammate (e.g. coolodu, jokerodu)")
    p_disp.add_argument("--type", choices=["token_heavy", "compute_heavy", "hybrid"], default="token_heavy", help="Bottleneck type")
    p_disp.add_argument("--title", required=True, help="Short summary of task")
    p_disp.add_argument("--brief", required=True, help="Detailed requirements and context")
    p_disp.add_argument("--priority", choices=["NORMAL", "HIGH", "URGENT"], default="NORMAL")
    p_disp.add_argument("--branch", default="main", help="Target branch for result hand-off")

    # list
    subparsers.add_parser("list", help="List all pending and completed tasks")

    # check
    p_check = subparsers.add_parser("check", help="Check for tasks assigned to a teammate")
    p_check.add_argument("--worker", required=True, help="Teammate username to check")

    # claim
    p_claim = subparsers.add_parser("claim", help="Claim a task from the inbox")
    p_claim.add_argument("--task", required=True, help="Task ID (e.g. TASK-001)")
    p_claim.add_argument("--worker", required=True, help="Your username")

    # complete
    p_comp = subparsers.add_parser("complete", help="Complete and archive a task")
    p_comp.add_argument("--task", required=True, help="Task ID (e.g. TASK-001)")
    p_comp.add_argument("--output", help="Path to delivered file/artifact")
    p_comp.add_argument("--notes", help="Completion notes")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "dispatch":
        cmd_dispatch(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "claim":
        cmd_claim(args)
    elif args.command == "complete":
        cmd_complete(args)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🛰️ Team RIP: GitHub Issues Bridge for Antigravity & Teammates
NASA Space Apps Challenge 2026 - Planet X & SPHEREx
Repository: joker0210G/spherex-hunter

Provides zero-dependency (pure Python stdlib) CLI integration with GitHub Issues:
- Query open issues anonymously via GitHub REST API
- Filter by worker / role (@coolodu, @darkodu, etc.)
- View issue details, checklists, and acceptance criteria
- Create new tasks (via API or pre-filled 1-click Web URL)
"""

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request

REPO = "joker0210G/spherex-hunter"
API_BASE = f"https://api.github.com/repos/{REPO}"
WEB_BASE = f"https://github.com/{REPO}"

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        import subprocess
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def _request(path, method="GET", data=None):
    url = f"{API_BASE}{path}"
    token = get_github_token()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TeamRIP-GitHub-Bridge"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return {"error": True, "status": e.code, "message": err_msg}
    except Exception as e:
        return {"error": True, "status": 0, "message": str(e)}

def check_worker_tasks(worker):
    role_label = f"role:{worker}"
    issues = _request("/issues?state=open")
    if isinstance(issues, dict) and issues.get("error"):
        print(f"❌ Failed to query GitHub Issues: {issues.get('message')}")
        return []

    assigned = []
    for iss in issues:
        # Ignore pull requests
        if "pull_request" in iss:
            continue

        labels = [l.get("name", "") for l in iss.get("labels", [])]
        assignees = [a.get("login", "") for a in iss.get("assignees", [])]
        body = iss.get("body") or ""

        if role_label in labels or worker in assignees or f"@{worker}" in body:
            assigned.append(iss)

    print(f"\n🔔 GitHub Issues Check for @{worker} on {REPO}:")
    if not assigned:
        print(f"   ✨ No open issues currently assigned to @{worker}!")
    else:
        print(f"   Found {len(assigned)} task(s):")
        for iss in assigned:
            track = next((l.get("name") for l in iss.get("labels", []) if l.get("name", "").startswith("track:")), "general")
            resource = next((l.get("name") for l in iss.get("labels", []) if l.get("name", "").startswith("resource:")), "")
            print(f"   📌 [#{iss['number']}] {iss['title']}")
            print(f"      Track: {track} | Resource: {resource} | URL: {iss['html_url']}")
    print("")
    return assigned

def list_issues(track_filter=None, status_filter=None):
    issues = _request("/issues?state=open")
    if isinstance(issues, dict) and issues.get("error"):
        print(f"❌ Failed to list GitHub Issues: {issues.get('message')}")
        return

    print(f"\n📋 Open Issues on {REPO}:")
    count = 0
    for iss in issues:
        if "pull_request" in iss:
            continue
        labels = [l.get("name", "") for l in iss.get("labels", [])]

        if track_filter and f"track:{track_filter}" not in labels and track_filter not in labels:
            continue
        if status_filter and f"status:{status_filter}" not in labels and status_filter not in labels:
            continue

        count += 1
        assignee_str = ", ".join([a.get("login", "") for a in iss.get("assignees", [])]) or "Unassigned"
        role_label = next((l for l in labels if l.startswith("role:")), None)
        if role_label:
            assignee_str = f"@{role_label.split(':', 1)[1]}"

        print(f"  #{iss['number']} {iss['title']}")
        print(f"     Owner: {assignee_str} | Labels: {', '.join(labels)}")
        print(f"     Link: {iss['html_url']}")

    if count == 0:
        print("  (No matching open issues found)")
    print("")

def view_issue(issue_number):
    iss = _request(f"/issues/{issue_number}")
    if isinstance(iss, dict) and iss.get("error"):
        print(f"❌ Failed to retrieve issue #{issue_number}: {iss.get('message')}")
        return

    labels = [l.get("name", "") for l in iss.get("labels", [])]
    print("\n=======================================================")
    print(f"📌 ISSUE #{iss['number']}: {iss['title']}")
    print(f"Status: {iss['state'].upper()} | URL: {iss['html_url']}")
    print(f"Labels: {', '.join(labels)}")
    print("=======================================================\n")
    print(iss.get("body") or "(No description provided)")
    print("\n=======================================================\n")

def create_issue(title, track, role, resource, body):
    token = get_github_token()
    labels = []
    if track: labels.append(f"track:{track}" if not track.startswith("track:") else track)
    if role: labels.append(f"role:{role}" if not role.startswith("role:") else role)
    if resource: labels.append(f"resource:{resource}" if not resource.startswith("resource:") else resource)
    labels.append("status:needs-refinement")

    if token:
        payload = {
            "title": title,
            "body": body,
            "labels": labels
        }
        res = _request("/issues", method="POST", data=payload)
        if res.get("error"):
            print(f"❌ Failed to create issue via API: {res.get('message')}")
        else:
            print(f"✅ Issue #{res['number']} created successfully!")
            print(f"🔗 Link: {res['html_url']}")
            return

    # Fallback to generating 1-click web creation URL
    params = {
        "title": title,
        "body": body,
        "labels": ",".join(labels)
    }
    web_url = f"{WEB_BASE}/issues/new?{urllib.parse.urlencode(params)}"
    print("\n🌐 Ready to create on GitHub:")
    print(f"Title: {title}")
    print(f"Labels: {', '.join(labels)}")
    print(f"\n🔗 Click to submit this issue on GitHub:\n{web_url}\n")

def close_issue(issue_number, comment=None):
    token = get_github_token()
    if not token:
        print("❌ Cannot close issue without GitHub token.")
        return
    if comment:
        _request(f"/issues/{issue_number}/comments", method="POST", data={"body": comment})
    res = _request(f"/issues/{issue_number}", method="PATCH", data={"state": "closed"})
    if isinstance(res, dict) and res.get("error"):
        print(f"❌ Failed to close issue #{issue_number}: {res.get('message')}")
    else:
        print(f"✅ Issue #{issue_number} successfully closed on GitHub!")

def reopen_issue(issue_number, comment=None):
    token = get_github_token()
    if not token:
        print("❌ Cannot reopen issue without GitHub token.")
        return
    if comment:
        _request(f"/issues/{issue_number}/comments", method="POST", data={"body": comment})
    res = _request(f"/issues/{issue_number}", method="PATCH", data={"state": "open"})
    if isinstance(res, dict) and res.get("error"):
        print(f"❌ Failed to reopen issue #{issue_number}: {res.get('message')}")
    else:
        print(f"✅ Issue #{issue_number} successfully reopened on GitHub!")

def main():
    parser = argparse.ArgumentParser(description="Team RIP GitHub Issues Bridge")
    subparsers = parser.add_subparsers(dest="command")

    # check
    check_parser = subparsers.add_parser("check", help="Check assigned issues for a teammate")
    check_parser.add_argument("--worker", required=True, help="Teammate name (coolodu, darkodu, iceodu, astrodu, jokerodu)")

    # list
    list_parser = subparsers.add_parser("list", help="List open issues")
    list_parser.add_argument("--track", help="Filter by track (feature-backend, web-frontend, uiux-pitch, image-math)")
    list_parser.add_argument("--status", help="Filter by status")

    # view
    view_parser = subparsers.add_parser("view", help="View issue details")
    view_parser.add_argument("--issue", type=int, required=True, help="Issue number")

    # close
    close_parser = subparsers.add_parser("close", help="Close an issue with optional comment")
    close_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    close_parser.add_argument("--comment", default=None, help="Closing comment")

    # reopen
    reopen_parser = subparsers.add_parser("reopen", help="Reopen a closed issue with optional comment")
    reopen_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    reopen_parser.add_argument("--comment", default=None, help="Reopening comment")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new task issue")
    create_parser.add_argument("--title", required=True, help="Issue title")
    create_parser.add_argument("--track", default="web-frontend", help="Track name")
    create_parser.add_argument("--role", default="coolodu", help="Teammate role")
    create_parser.add_argument("--resource", default="token-heavy", help="Resource profile (token-heavy, compute-heavy, standard)")
    create_parser.add_argument("--body", default="Task specification...", help="Issue body / spec")

    args = parser.parse_args()
    if args.command == "check":
        check_worker_tasks(args.worker)
    elif args.command == "list":
        list_issues(track_filter=args.track, status_filter=args.status)
    elif args.command == "view":
        view_issue(args.issue)
    elif args.command == "close":
        close_issue(args.issue, comment=args.comment)
    elif args.command == "reopen":
        reopen_issue(args.issue, comment=args.comment)
    elif args.command == "create":
        create_issue(args.title, args.track, args.role, args.resource, args.body)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

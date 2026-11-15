#!/usr/bin/env python3
"""
🛰️ Team RIP: 1-Click Multi-Track Team Radar & Sync Summary
NASA Space Apps Challenge 2026 - Planet X & SPHEREx
Repository: joker0210G/spherex-hunter

Provides a beginner-friendly terminal dashboard summarizing:
- What each teammate recently committed across all 5 branches
- Active GitHub Issues & Task Assignments
- Latest announcements from SHARED_PROJECT_STATE.md
"""

import os
import re
import subprocess
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATE_FILE = os.path.join(BASE_DIR, "07 - Team Memory & Sync", "SHARED_PROJECT_STATE.md")

BRANCHES = [
    ("main", "jokerodu (Lead)", "Architecture & Golden Suite"),
    ("origin/darkodu/astro-backend", "darkodu", "Astro-Data / IRSA / TAP"),
    ("origin/coolodu/web-frontend", "coolodu", "60 FPS Viewport & UI"),
    ("origin/iceodu/image-math-ai", "iceodu", "Image Math & PSF Convolutions"),
    ("origin/astrodu/ui-story-pitch", "astrodu", "UI/UX, Story & Pitch Video"),
]

def run_git(cmd):
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def get_current_branch():
    return run_git(["git", "branch", "--show-current"]) or "main"

def get_branch_latest_commits(branch_ref, count=2):
    log_out = run_git(["git", "log", branch_ref, f"-n{count}", "--format=%h|%an|%ar|%s"])
    if not log_out:
        return []
    commits = []
    for line in log_out.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "time": parts[2],
                "msg": parts[3]
            })
    return commits

def get_open_github_issues():
    # Use github_bridge logic
    try:
        sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
        import github_bridge
        issues = github_bridge._request("/issues?state=open")
        if isinstance(issues, list):
            return [iss for iss in issues if "pull_request" not in iss]
    except Exception:
        pass
    return []

def get_recent_announcements(max_items=3):
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    announcements = []
    log_match = re.search(r"## 📝 Recent Team Log & Announcements\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if log_match:
        items = re.findall(r"-\s+\*\*\[(.*?)\]\*\*(.*?)(?=\n-\s+\*\*|\Z)", log_match.group(1), re.DOTALL)
        for title, body in items[:max_items]:
            clean_body = " ".join(body.strip().splitlines())
            if len(clean_body) > 140:
                clean_body = clean_body[:137] + "..."
            announcements.append((title, clean_body))
    return announcements

def print_banner():
    current_branch = get_current_branch()
    print("=" * 78)
    print("🛰️  TEAM RIP: MULTI-TRACK LIVE RADAR & SYNC DASHBOARD")
    print("    NASA Space Apps Challenge 2026 | Challenge: Planet X & SPHEREx")
    print("=" * 78)
    print(f"📍 Your Current Branch: [{current_branch}]")
    print("-" * 78)

def print_team_activity():
    print("\n👥 WHAT EACH TEAMMATE RECENTLY WORKED ON (All Branches):")
    print("-" * 78)
    for branch_ref, owner, focus in BRANCHES:
        commits = get_branch_latest_commits(branch_ref, count=2)
        print(f"🔹 {owner:<18} [{branch_ref}]")
        print(f"   Domain: {focus}")
        if not commits:
            print("   (No local commits found - run git fetch)")
        else:
            for c in commits:
                print(f"   • [{c['hash']}] {c['time']} by {c['author']}")
                print(f"     \"{c['msg']}\"")
        print("")

def print_github_issues():
    print("📋 ACTIVE GITHUB ISSUES & TASKS:")
    print("-" * 78)
    issues = get_open_github_issues()
    if not issues:
        print("  ✨ All tasks verified or no open issues found on GitHub!")
    else:
        for iss in issues:
            labels = [l.get("name", "") for l in iss.get("labels", [])]
            track = next((l for l in labels if l.startswith("track:")), "track:general")
            role = next((l for l in labels if l.startswith("role:")), "role:unassigned")
            resource = next((l for l in labels if l.startswith("resource:")), "")
            print(f"  📌 [#{iss['number']}] {iss['title']}")
            print(f"     Assigned: @{role.replace('role:', '')} | {track} | {resource}")
            print(f"     URL: {iss['html_url']}")
    print("")

def print_announcements():
    print("📢 LATEST ANNOUNCEMENTS FROM CENTRAL LEDGER:")
    print("-" * 78)
    announcements = get_recent_announcements(3)
    if not announcements:
        print("  (No recent log items found)")
    else:
        for title, body in announcements:
            print(f"  ⚡ [{title}]")
            print(f"     {body}\n")

def main():
    print_banner()
    print_team_activity()
    print_github_issues()
    print_announcements()
    print("=" * 78)
    print("💡 TIP: Your local workspace is now synchronized with GitHub!")
    print("   Open Antigravity IDE and start coding, or review issues on GitHub.")
    print("=" * 78)

if __name__ == "__main__":
    main()

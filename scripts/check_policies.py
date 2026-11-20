#!/usr/bin/env python3
"""Checks the policy files against the Task 02 rules. Run: python3 scripts/check_policies.py"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "policies"
PLACEHOLDERS = {"<ACCOUNT_ID>", "<REGION>", "<BUCKET>", "<INSTANCE_ID>", "<LOG_GROUP>"}
errors, notes = [], []

def err(path, msg):
    errors.append(f"{path.relative_to(ROOT.parent)}: {msg}")

def as_list(x):
    return x if isinstance(x, list) else [x]

role_dirs = sorted(p for p in ROOT.iterdir() if p.is_dir())
if len(role_dirs) < 3:
    errors.append(f"need at least 3 roles, found {len(role_dirs)}")

for d in role_dirs:
    for name in ("trust.json", "permissions.json", "cannot-do.md"):
        if not (d / name).exists():
            errors.append(f"{d.name}: missing {name}")
    cannot = d / "cannot-do.md"
    if cannot.exists() and cannot.read_text().count("\n- ") < 2:
        err(cannot, "list at least two things the role cannot do")

    perm = d / "permissions.json"
    if perm.exists():
        doc = json.loads(perm.read_text())
        if doc.get("Version") != "2012-10-17":
            err(perm, "Version must be 2012-10-17")
        for st in as_list(doc["Statement"]):
            sid = st.get("Sid")
            if not sid:
                err(perm, "every statement needs a Sid")
                continue
            if st.get("Effect") != "Allow":
                err(perm, f"{sid}: only Allow statements expected")
            for a in as_list(st.get("Action", [])):
                if "*" in a:
                    err(perm, f"{sid}: wildcard action '{a}'")
            for r in as_list(st.get("Resource", [])):
                if r == "*":
                    if not sid.startswith("NoResourceLevel"):
                        err(perm, f"{sid}: Resource '*' only allowed for Sids starting NoResourceLevel")
                    else:
                        notes.append(f"{d.name}/{sid}: Resource '*' (no resource-level support for: {', '.join(as_list(st['Action']))})")
                elif "*" in r and not re.fullmatch(r"[^*]+(/\*|:\*)", r):
                    err(perm, f"{sid}: unexpected wildcard in resource '{r}'")
            for ph in re.findall(r"<[A-Z_]+>", json.dumps(st)):
                if ph not in PLACEHOLDERS:
                    err(perm, f"{sid}: unknown placeholder {ph}")

    trust = d / "trust.json"
    if trust.exists():
        doc = json.loads(trust.read_text())
        for st in as_list(doc["Statement"]):
            principal = st.get("Principal")
            if principal == "*" or (isinstance(principal, dict) and principal.get("AWS") == "*"):
                err(trust, "Principal must not be '*'")
            if st.get("Action") != "sts:AssumeRole":
                err(trust, "trust action must be sts:AssumeRole")

print(f"Roles checked: {', '.join(d.name for d in role_dirs)}")
for n in notes:
    print("  note:", n)
if errors:
    print("\nFAILED")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("\nOK: no wildcard actions, no unexplained wildcard resources, every role has a cannot-do note.")

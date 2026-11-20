#!/usr/bin/env python3
"""Fills in the placeholders and writes ready-to-use JSON to build/.
Example:
  python3 scripts/render.py --account-id 123456789012 --region us-east-1 \
      --bucket my-nova-bucket --instance-id i-0abc123def4567890 --log-group /nova/app
"""
import argparse, json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--account-id", required=True)
p.add_argument("--region", required=True)
p.add_argument("--bucket", required=True)
p.add_argument("--instance-id", required=True)
p.add_argument("--log-group", default="/nova/app")
a = p.parse_args()
values = {"<ACCOUNT_ID>": a.account_id, "<REGION>": a.region, "<BUCKET>": a.bucket,
          "<INSTANCE_ID>": a.instance_id, "<LOG_GROUP>": a.log_group}

root = Path(__file__).resolve().parent.parent
out = root / "build"
for src in sorted((root / "policies").glob("*/*.json")):
    text = src.read_text()
    for k, v in values.items():
        text = text.replace(k, v)
    json.loads(text)  # make sure it is still valid JSON
    dest = out / src.parent.name / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
    print("wrote", dest.relative_to(root))

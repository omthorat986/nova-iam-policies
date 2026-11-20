# NOVA – IAM permission policies (Task 02)

Least-privilege IAM policies for one application (**NOVA**, a Flask website on one EC2 server with an S3 bucket and CloudWatch) and a small team.

## What is in here

| Role | Who uses it | Can do | Details |
|---|---|---|---|
| `NovaAppRole` | The EC2 server (instance profile) | Read/write `uploads/`, write `backups/`, write its own logs, send agent metrics | [cannot-do](policies/nova-app/cannot-do.md) |
| `NovaDeveloperRole` | Developers | Read/write `deploy/`, read logs and metrics, see instance status | [cannot-do](policies/nova-developer/cannot-do.md) |
| `NovaOperatorRole` | Whoever keeps it running | Start/stop/reboot the one NOVA instance, read backups to restore, see alarms | [cannot-do](policies/nova-operator/cannot-do.md) |
| `NovaAuditorRole` | Reviewer (read-only) | Read the roles' policies, bucket settings, logs, alarms | [cannot-do](policies/nova-auditor/cannot-do.md) |

Each folder under `policies/` holds:
- `trust.json`: who may assume the role
- `permissions.json`: what the role may do
- `cannot-do.md`: what the role deliberately cannot do, and why

## The rules I followed

**How I read "no wildcard actions on resources".** The brief is short, so I applied the strictest reading:
1. No `"Action": "*"` and no `service:*` or `Describe*`-style actions anywhere. Every action is spelled out.
2. `"Resource": "*"` is used **only** where AWS does not support resource-level permissions for that action (for example `cloudwatch:PutMetricData`, `ec2:DescribeInstances`). Those statements have a Sid starting `NoResourceLevel`, and the checker script allows `*` only for them.
3. Everything else names an exact ARN. The only `*` inside an ARN is the standard ending that means "objects under this prefix" (`/uploads/*`) or "streams in this log group" (`:*`).

If the reviewer meant something different, that is the one point I would confirm through a support ticket.

## How to run it

Requires Python 3 only (no packages).

```bash
# 1. Check the policies against the rules above
python3 scripts/check_policies.py

# 2. Fill in your own values (writes to build/, which is git-ignored)
python3 scripts/render.py --account-id 123456789012 --region us-east-1 \
    --bucket your-nova-bucket --instance-id i-0abc123def4567890 --log-group /nova/app
```

Placeholders in the files: `<ACCOUNT_ID>`, `<REGION>`, `<BUCKET>`, `<INSTANCE_ID>`, `<LOG_GROUP>`.

### Optional: create a role in AWS (after step 2)

```bash
aws iam create-role --role-name NovaDeveloperRole \
  --assume-role-policy-document file://build/nova-developer/trust.json \
  --max-session-duration 3600

aws iam put-role-policy --role-name NovaDeveloperRole --policy-name NovaDeveloperAccess \
  --policy-document file://build/nova-developer/permissions.json
```

For `NovaAppRole`, also create an instance profile and attach the role to the server. For the human roles, give each team member's group a policy that allows only `sts:AssumeRole` on the matching role ARN.

To double-check a policy with AWS's own validator:

```bash
aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY \
  --policy-document file://build/nova-app/permissions.json
```

## Decisions I made

- **Separate roles for separate jobs.** Developers ship code, operators run the server, and neither reads user data. Nobody has more access than their task needs.
- **S3 prefixes split the data by sensitivity.** `uploads/` (user data), `backups/` (database copies), `deploy/` (code). Each role sees only the prefixes it needs.
- **No delete permissions anywhere.** Accidents and attackers cannot erase data. Cleanup is a deliberate admin action outside these roles.
- **The app can write backups but not read them.** A stolen server cannot leak old database copies.
- **MFA on human roles.** The trust policy requires `aws:MultiFactorAuthPresent`. The trade-off: people must sign in with MFA before assuming a role.
- **Operator can start, stop and reboot, not terminate.** Terminating is irreversible.
- **No `iam:*` for anyone.** Nobody here can grant themselves more access. The auditor can only read the four NOVA roles.
- **The log group is created in advance.** The roles can write to it but cannot create log groups, which keeps the policy smaller.

## Known limits

- These are identity policies only. In production I would add a permissions boundary and an S3 bucket policy as a second lock.
- The trust policy uses the account root as principal plus MFA. Real access is then controlled by which groups may call `sts:AssumeRole` on each role.
- Names are NOVA-specific. Rename the roles to match any you already have, and update the four ARNs in `nova-auditor/permissions.json`.

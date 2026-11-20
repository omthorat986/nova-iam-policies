# NovaAppRole – what it deliberately cannot do

The NOVA server runs this role. If the server is hacked, these limits cap the damage.

- **Cannot delete anything in S3.** There is no `s3:DeleteObject`, so an attacker cannot wipe user images or backups.
- **Cannot read backups.** It can only write to `backups/`, so stolen server access does not expose database copies.
- **Cannot touch `deploy/`.** Code artifacts are not reachable, so it cannot swap in tampered code.
- **Cannot use any other bucket, or the rest of the bucket.** Access is limited to `uploads/` and `backups/`.
- **Cannot call IAM, EC2, SNS or any other service.** It cannot create users, change its own permissions, or stop servers.
- **Cannot write metrics outside the `CWAgent` namespace**, and cannot read logs from other log groups.

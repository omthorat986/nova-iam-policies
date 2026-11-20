# NovaOperatorRole – what it deliberately cannot do

For the person who keeps the server running.

- **Cannot terminate the instance.** Only start, stop and reboot are allowed, so the server cannot be destroyed by accident.
- **Cannot control any instance except the NOVA one.** The resource is a single instance ARN.
- **Cannot change the instance, its security group, or its volumes.** Network and disk layout stay fixed.
- **Cannot read user uploads or deploy artifacts.** It reads `backups/` only, to restore the database.
- **Cannot delete or overwrite backups.** Read-only on that prefix.
- **Cannot deploy code or change IAM.**

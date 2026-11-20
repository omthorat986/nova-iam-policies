# NovaDeveloperRole – what it deliberately cannot do

For people who ship code and debug problems.

- **Cannot read user uploads or backups.** Developers see only `deploy/`, so private user data stays private.
- **Cannot delete deploy files.** There is no `s3:DeleteObject`, so a mistaken command cannot erase release history.
- **Cannot start, stop, reboot or modify the server.** That is the operator's job, which keeps changes to running infrastructure accountable.
- **Cannot change IAM, security groups or alarms.** It cannot widen its own access.
- **Cannot write logs or metrics.** It is read-only for observability.

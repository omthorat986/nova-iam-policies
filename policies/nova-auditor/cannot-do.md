# NovaAuditorRole – what it deliberately cannot do

For a reviewer, teacher or security check. Strictly read-only.

- **Cannot read any S3 object.** It can inspect bucket settings (policy, public access block, encryption, versioning) but not the files.
- **Cannot change anything.** There are no write, create, delete, start or stop actions.
- **Cannot read other roles' policies.** It reads only the four NOVA roles.
- **Cannot read the logs of any other log group.**

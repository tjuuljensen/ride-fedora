For the remaining migration, I’ll apply a tighter approach:
- Define the completion criteria before testing.
- Run focused automated tests and reuse valid evidence for unchanged components.
- Use one brief manual session only where user-visible behavior needs it; automate preparation, collection and recovery.
- Keep deeper coverage for higher-risk changes involving data, storage, encryption or security.
- Treat optional additions and unsupported scenarios separately from migration blockers. Investigate failures before retrying.
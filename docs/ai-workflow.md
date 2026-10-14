# AI-assisted v3 development

Use `AGENTS.md` as the repository contract. For one legacy function, invoke
the `ride-operation-migration` skill and provide its source, expected user
outcome, and target profile. Ask the agent to inspect current upstream and
Fedora package facts, propose a stable catalog ID, implement a trusted
handler, and add a mocked lifecycle test. The agent should then update the
76-entry migration ledger or Sander map and regenerate `docs/OPERATIONS.md`.

Useful review prompts:

1. “Compare this catalog entry with its upstream package and license page;
   report inaccurate identity, source, or verification claims.”
2. “Review this handler for idempotence, prior-state ownership, failure
   journaling, unsafe paths, and exact restore behavior.”
3. “Generate failure scenarios for the mocked provider and tell me which
   observable assertions the tests are missing.”
4. “Review the Fedora Workstation and Server VM transcript against the
   acceptance record template, without inferring untested platforms.”

AI drafts accelerate inventory, tests, and review. CI checks syntax, schema,
generated documentation, mocked behavior, and Firefox policy. Disposable VM
results determine whether a candidate becomes supported. Keep VM logs and
source facts with the acceptance record; a successful mocked test does not
certify installation on a real distro.

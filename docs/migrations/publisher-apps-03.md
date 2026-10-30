# VS Code and Brave publisher repositories

Status: **two unsupported v3.0 operations**, 2026-10-30. This related
active-preset batch preserves `InstallVisualStudioCode` / `RemoveVisualStudioCode`
and `InstallBrave` / `RemoveBrave` as separate product outcomes. Both v2
installers add a publisher repository and an RPM. VS Code's inverse also
removes a hard-coded global GPG key ID, which may be shared; Brave's inverse
leaves its repository behind.
The owner kept Visual Studio Code in the v3.0 fast-track review. Its owned
publisher repository and package lifecycle remain to implement.

## Completion criteria defined before implementation

- Bind each product to its publisher's current Fedora 44 repository, key,
  package identity, license, and exact target. Verify the key or RPM
  signature and prevent replacing an unowned repository or key.
- A v3 handler must detect the installed package and repository separately,
  record which it created, preserve existing package/user data, and remove
  only its owned package/repository/key state. Mock conflicts and failure
  cleanup. A disposable Fedora 44 x86_64 Workstation VM must pass plan,
  apply, repeat, status, restore/remove, signed RPM inspection, and an
  application startup probe before an opt-in candidate is operable.
- Defer broader desktop and update behavior to v3.1 only after that happy
  path; keep candidates out of base profiles.

[Microsoft's Linux instructions](https://code.visualstudio.com/docs/setup/linux)
publish the `code` RPM repository and signing key for Fedora. [Brave's
Fedora 41+ instructions](https://brave.com/linux/) publish a separate
`brave-browser` repository through DNF5. Those are genuine publisher routes,
but the current v3 catalog/engine supports Fedora's signed repository
packages, not owned external repository/key lifecycles. Reusing the v2
hard-coded key deletion or leaving a repository behind would violate its
inverse contract. No exact-target VM install or recovery has been run for
these publisher packages. Both source outcomes are **non-runnable
unsupported in v3.0**. Reopen together when an external-repository handler
and the focused evidence above are ready. Windows has a separately accepted
VS Code **user setup** deployment, which shares product identity but not
the Fedora system RPM installer or recovery.

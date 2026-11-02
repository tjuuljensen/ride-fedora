# Provider foundation batch 03: kernel, DNF, Python, and archive tools

Status: **DNF5 replacement recorded; kernel, Python, and archive package
paths supported**, reviewed 2026-10-31.
The owner kept DNFutils for migration and specified replacement with DNF5 on
2026-10-30. PackagingTools also remains in scope. The accepted
7zip and unar lifecycles remain valid; the later
[unrar wrapper follow-up](provider-foundation-03-unrar.md) restores the
command choice through a separate supported RPM.
Four active v2 bundle outcomes remain after moving Flathub remote ownership
to [its own batch](provider-foundation-09.md).

| v2 outcome | Current Fedora 44 treatment |
| --- | --- |
| `KernelTools` | Split `kernel-devel` and `kernel-headers` into exact Fedora RPM operations. They install build files, not a guarantee that they match the running kernel. [kernel-devel](https://packages.fedoraproject.org/pkgs/kernel/kernel-devel/), [kernel-headers](https://packages.fedoraproject.org/pkgs/kernel-headers/kernel-headers/) |
| `DNFutils` | The v2 `dnf-utils` package is a DNF4-era bundle. Fedora 44 ships [DNF5](https://packages.fedoraproject.org/pkgs/dnf5/dnf5/) and [DNF5 plugins](https://packages.fedoraproject.org/pkgs/dnf5/dnf5-plugins/) on the pinned Workstation image; its `download` and `config-manager` commands passed read-only checks on the declared target and have [current DNF5 documentation](https://dnf5.readthedocs.io/en/stable/dnf5.8.html). Record DNF5 as the v3 replacement; do not install the obsolete bundle or change repository configuration. |
| `PythonPip` | Replace the v2 `python-pip` RPM and unscoped `pip install --upgrade pip` with Fedora's signed [python3-pip](https://packages.fedoraproject.org/pkgs/python-pip/python3-pip/) RPM. Do not mutate the system Python environment after DNF installation. |
| `PackagingTools` | Fedora 44 no longer lists a `p7zip` build; Fedora [7zip](https://packages.fedoraproject.org/pkgs/7zip/7zip/) and the [unrar-free wrapper](https://packages.fedoraproject.org/pkgs/unrar-free/unrar/) now provide an operable v3 path for the archive and `unrar` commands. [Unar](https://packages.fedoraproject.org/pkgs/unar/unar/) remains an independent extractor option. |

## Completion criteria defined before implementation

- For `KernelTools` and `PythonPip`, record Fedora package license/source,
  exact target, product, installed destination, signed RPM verification, and
  declared inverse. Keep these out of base profiles. Reuse the unchanged
  DNF handler's focused mocked failure tests.
- In one disposable Fedora 44 x86_64 Workstation VM, check each new RPM's
  absent plan, apply, repeat, status, signature/files, command or package
  presence, restore, and explicit remove. Preserve pre-existing RPM
  name/architecture identities; record package-driven updates and retained
  dependencies. For kernel packages, record the running kernel and installed
  `kernel-devel` version without asserting module-build compatibility.
- Count `KernelTools` as supported only if both RPM operations pass; count
  `PythonPip` as supported only if its RPM passes and no global pip upgrade
  occurs. A failure is investigated before retrying.
- Resolve `DNFutils` by documenting the current DNF5/plugin commands on the
  declared target and confirming the v3 provider uses current DNF behavior;
  the replacement does not add a package install or alter repository state.
- For `PackagingTools`, add independent Fedora `package.7zip` and
  `package.unar` operations. In a disposable Workstation VM, verify that
  removing pre-installed `7zip` for the test affects no other pre-existing
  RPM; then run the same absent package lifecycle for both operations.
  Record that `unar` is not a drop-in `unrar` executable. Count the v2
  bundle as a documented replacement, separately from runnable source
  outcomes, after both new operations pass.
- Record Windows alignment, ledger status, generated docs, and any v3.1
  follow-up separately from the v3.0 result.

## DNF5 utility replacement

The v2 `dnf-utils` install/remove pair is replaced by Fedora 44's DNF5 and
DNF5 plugins. In disposable Workstation overlay
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`,
`rpm -q dnf5 dnf5-plugins`, `dnf5 config-manager --help`, and
`dnf5 download --help` all passed before any package change. The v3 client
uses current DNF commands and does not install the obsolete v2 bundle or
alter repository configuration to supply it. This is the completed DNFutils
replacement for the declared Fedora 44 Workstation target. Revisit if DNF5
plugin availability or the declared Fedora target changes.

## Package VM results

The focused kernel/Python VM run passed in disposable overlay
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`,
catalog SHA-256
`819b73be3d9d30dec5dfcf9fdd9b2be5013443cf471a33026fdb0ee556897a9c`.
[`package.kernel-devel` and `package.kernel-headers`](../acceptance/provider-kernel-tools.md)
and [`package.python3-pip`](../acceptance/package.python3-pip.md) each passed
absent plan, apply, signed RPM and file verification, status, unchanged
repeat, restore, and explicit remove. `kernel-devel` introduced 13 RPM
identities and updated 14 pre-existing RPM versions, including glibc,
elfutils, GCC runtime, and OpenSSL packages; the inverse removed the newly
installed RPMs without downgrading the DNF updates. The running kernel was
`6.19.10-300.fc44.x86_64`, while installed `kernel-devel` was
`7.2.13-200.fc44.x86_64`. Package installation is supported; matching
module-build behavior is a separate v3.1 review. `kernel-headers` and
`python3-pip` returned the full RPM inventory to baseline.

The archive VM run passed in disposable overlay
`20261030T113943Z-test-provider-archive-replacement-batch-ba654452`,
catalog SHA-256
`82463b1b2773ce73896b5b6f04ea24f186160caaf3b0846050c6a84023f5e086`.
Test preparation removed only the pre-installed `7zip` RPM. Fedora
[`package.7zip` and `package.unar`](../acceptance/provider-archive-tools.md)
then passed separate absent package lifecycles, with complete inventory
recovery. The v2 `PackagingTools` bundle is recorded as a **documented,
non-runnable replacement** because `unar` changes the `unrar` command and
Fedora 44 no longer has the selected `p7zip` package. The two new operations
are individually supported, but this original batch did not count the source
outcome as an unchanged working v2 install. The later
[unrar wrapper acceptance](../acceptance/package.unrar.md) closes that
command-name gap and makes the source outcome operable through an opt-in
profile. H026 retains wider RAR feature compatibility checks.

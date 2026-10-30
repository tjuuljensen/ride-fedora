# System and security batch 29: KeePassXC package and vault safety

Status: **unresolved**, 2026-10-30. The v2 pair only installs and removes
the Fedora `keepassxc` RPM. The v3 operation must keep encrypted user vaults,
keys, and application configuration outside RIDE ownership. Review the
current Fedora source and license, detection, install/removal effects, and
disposable-VM evidence that user data is untouched before making this
encryption-related application runnable. Do not claim a vault recovery path
from a package transaction.

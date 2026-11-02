# YubiKey personalization tool replacement

The owner kept the YubiKey personalization capability in v3.0. The v2 path
builds an unpinned Qt4 GUI from source and has no remove function. The archived
GUI is not installed directly in v3. The current Yubico path is the
Yubico Authenticator GUI plus the maintained `ykman` CLI, handled separately
from hardware configuration.

Status: **shared Fedora CLI supported; Authenticator GUI is an operable opt-in candidate**,
2026-11-01. This commented-source outcome maps
`InstallYubikeyPersTool`; profile selection does not change whether the
function is in scope.

See [Publisher Apps 08](publisher-apps-08.md) for current source, license,
release digest, bounded implementation criteria, and the supported Fedora 44
`ykman` package operation. The signed GUI archive now has an independently owned user-scoped lifecycle.
Its Fedora 44 Workstation acceptance passed without modifying user preferences
or connected key data. The package operation does not launch the GUI or change
key state. Hardware and visible GUI behavior remain outside the v3.0 claim;
see H072 in the v3.1 queue.

"""Journal and restore coverage for Firefox's restart-pending removal state."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "ride.sh"


class FirefoxAddonEngineTests(unittest.TestCase):
    def test_remove_is_pending_until_explicit_absence_and_can_be_restored(self):
        with tempfile.TemporaryDirectory(prefix="ride-firefox-engine-") as temporary:
            root = Path(temporary)
            state = root / "state"
            runs = root / "runs"
            entry = {
                "id": "setting.firefox-addons",
                "kind": "setting",
                "name": "Firefox extensions",
                "group": "desktop-user",
                "description": "test fixture",
                "handler": "firefox-extensions",
                "states": ["configured", "removal-pending", "absent"],
                "scope": "system",
                "status": "candidate",
                "recovery": "exact-state",
                "targets": {"fedora": {"releases": ["44"], "architectures": ["x86_64"]}},
                "productId": "firefox",
                "productUri": "https://www.mozilla.org/firefox/",
                "license": "MPL-2.0",
                "licenseUri": "https://www.mozilla.org/en-US/MPL/2.0/",
                "sourceUri": "https://mozilla.github.io/policy-templates/#extensions",
                "verification": "local-owned-firefox-extension-policy",
            }
            entry_path = root / "entry.json"
            entry_path.write_text(json.dumps(entry), encoding="utf-8")
            state.write_text("configured\n", encoding="utf-8")
            script = f"""
set -euo pipefail
source {str(CLI)!r}
RIDE_STATE_DIR={str(runs)!r}
RIDE_DRY_RUN=0
ride_entry_or_die() {{ cat {str(entry_path)!r}; }}
ride_source_signature() {{ printf 'test-signature\\n'; }}
ride_require_target() {{ :; }}
ride_require_accepted() {{ :; }}
ride_require_privilege() {{ :; }}
ride_dependencies_ready() {{ :; }}
ride_observe() {{ cat {str(state)!r}; }}
ride_change() {{
  case "$2:$(cat {str(state)!r})" in
    absent:configured) printf 'removal-pending\\n' > {str(state)!r} ;;
    absent:removal-pending) printf 'absent\\n' > {str(state)!r} ;;
    configured:removal-pending) printf 'configured\\n' > {str(state)!r} ;;
    *) printf 'unexpected transition %s from %s\\n' "$2" "$(cat {str(state)!r})" >&2; return 31 ;;
  esac
}}
ride_apply_single setting.firefox-addons absent
pending_id=$RIDE_RUN_ID
jq -e '.status == "pending" and .steps[0].result == "pending" and
  .steps[0].observedAfter == "removal-pending"' "$(ride_journal_by_id "$pending_id")" >/dev/null
ride_restore "$pending_id"
[[ "$(cat {str(state)!r})" == configured ]]
jq -e '.status == "complete"' "$(ride_journal_by_id "$RIDE_RUN_ID")" >/dev/null
ride_apply_single setting.firefox-addons absent
[[ "$(cat {str(state)!r})" == removal-pending ]]
# The simulated browser restart leaves the RIDE marker pending until finalize.
ride_apply_single setting.firefox-addons absent
[[ "$(cat {str(state)!r})" == absent ]]
jq -e '.status == "complete" and .steps[0].observedAfter == "absent"' \\
  "$(ride_journal_by_id "$RIDE_RUN_ID")" >/dev/null
"""
            result = subprocess.run(
                ["bash", "-c", script],
                env=os.environ.copy(),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("pending setting.firefox-addons", result.stdout)


if __name__ == "__main__":
    unittest.main()

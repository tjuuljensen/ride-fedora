"""Owned GNOME custom shortcut lifecycle and scoped recovery."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
CATALOG = ROOT / "lib/v3/catalog.sh"
MEDIA = "org.gnome.settings-daemon.plugins.media-keys"
WM = "org.gnome.desktop.wm.keybindings"
BASE = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
USER_PATH = f"{BASE}/custom100/"


class GnomeCustomShortcutsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-gnome-shortcuts-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.xdg = self.root / "data"
        self.config = json.dumps({
            "global": {
                "showDesktop": ["<Super>d"],
                "switchWindows": ["<Alt>Tab"],
            },
            "shortcuts": [{
                "name": "Files home",
                "command": "nautilus",
                "binding": "<Super>e",
            }],
        }, separators=(",", ":"))
        self.entry = json.dumps({
            "id": "setting.gnome-custom-shortcuts",
            "selectedValue": self.config,
            "valueKind": "custom-shortcut-list",
        })

    def shell(self, body, *, paths=None, show=None, switch=None, extra=""):
        paths = paths or f"['{USER_PATH}']"
        show = show or "['<Control>Escape']"
        switch = switch or "['<Alt>Tab']"
        script = f"""set -euo pipefail
source {CATALOG}
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_require_command() {{ :; }}
declare -A GNOME_VALUES
GNOME_VALUES['{MEDIA}|custom-keybindings']={json.dumps(paths)}
GNOME_VALUES['{WM}|show-desktop']={json.dumps(show)}
GNOME_VALUES['{WM}|switch-windows']={json.dumps(switch)}
GNOME_VALUES['{MEDIA}.custom-keybinding:{USER_PATH}|name']='User shortcut'
GNOME_VALUES['{MEDIA}.custom-keybinding:{USER_PATH}|command']='user-command'
GNOME_VALUES['{MEDIA}.custom-keybinding:{USER_PATH}|binding']='<Super>u'
FAIL_ONCE=1
ride_gsettings() {{
  local action=$1 schema=$2 key=$3 value=${{4:-}} identity
  if [[ "$schema" == *:* ]]; then
    identity="$schema|$key"
  else
    identity="$schema|$key"
  fi
  case "$action" in
    get) printf '%s\\n' "${{GNOME_VALUES[$identity]:-''}}" ;;
    writable) printf 'true\\n' ;;
    range) printf 'type as\\n' ;;
    set)
      if [[ -n "${{TEST_FAIL_KEY:-}}" && "$key" == "$TEST_FAIL_KEY" && "$FAIL_ONCE" == 1 ]]; then
        FAIL_ONCE=0; return 1
      fi
      GNOME_VALUES[$identity]=$value
      ;;
    reset) unset 'GNOME_VALUES[$identity]' ;;
    *) printf 'unexpected gsettings call: %s\\n' "$*" >&2; return 2 ;;
  esac
}}
{extra}
{body}
"""
        env = os.environ.copy()
        env["XDG_DATA_HOME"] = str(self.xdg)
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_configured_repeat_remove_preserves_prior_user_shortcut_state(self):
        result = self.shell(
            'ride_gnome_custom_shortcuts_observe "$TEST_ENTRY"\n'
            'ride_gnome_custom_shortcuts_change "$TEST_ENTRY" configured\n'
            'ride_gnome_custom_shortcuts_observe "$TEST_ENTRY"\n'
            'ride_gnome_custom_shortcuts_change "$TEST_ENTRY" configured\n'
            'ride_gnome_custom_shortcuts_change "$TEST_ENTRY" absent\n'
            'ride_gnome_custom_shortcuts_observe "$TEST_ENTRY"\n'
            'printf "paths=%s\\n" "${GNOME_VALUES[\'' + MEDIA + '|custom-keybindings\']}"\n'
            'printf "show=%s\\n" "${GNOME_VALUES[\'' + WM + '|show-desktop\']}"\n'
            'printf "switch=%s\\n" "${GNOME_VALUES[\'' + WM + '|switch-windows\']}"\n'
            'printf "user=%s\\n" "${GNOME_VALUES[\'' + MEDIA + '.custom-keybinding:' + USER_PATH + '|name\']}"',
            extra='TEST_ENTRY=' + json.dumps(self.entry),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "absent", "configured", "absent",
            f"paths=['{USER_PATH}']",
            "show=['<Control>Escape']",
            "switch=['<Alt>Tab']",
            "user=User shortcut",
        ])
        self.assertFalse((self.xdg / "ride-fedora/owned/setting.gnome-custom-shortcuts.json").exists())

    def test_external_edit_to_owned_shortcut_blocks_removal(self):
        body = ('ride_gnome_custom_shortcuts_change "$TEST_ENTRY" configured\n'
                'owner=$(ride_gnome_shortcuts_owner_file)\n'
                'path=$(jq -r ".entries[0].path" "$owner")\n'
                'GNOME_VALUES["' + MEDIA + '.custom-keybinding:$path|binding"]="<Super>x"\n'
                'ride_gnome_custom_shortcuts_change "$TEST_ENTRY" absent')
        result = self.shell(body, extra='TEST_ENTRY=' + json.dumps(self.entry))
        self.assertEqual(result.returncode, 42)
        self.assertIn("changed outside RIDE", result.stderr)

    def test_unsafe_ownership_record_permissions_block_observe(self):
        result = self.shell(
            'ride_gnome_custom_shortcuts_change "$TEST_ENTRY" configured\n'
            'owner=$(ride_gnome_shortcuts_owner_file)\n'
            'chmod 0644 "$owner"\n'
            'ride_gnome_custom_shortcuts_observe "$TEST_ENTRY"',
            extra='TEST_ENTRY=' + json.dumps(self.entry),
        )
        self.assertEqual(result.returncode, 42)
        self.assertIn("unsafe owner or permissions", result.stderr)

    def test_failed_apply_rolls_back_global_and_owned_slot_changes(self):
        result = self.shell(
            'ride_gnome_custom_shortcuts_change "$TEST_ENTRY" configured',
            extra='TEST_ENTRY=' + json.dumps(self.entry) + '\nTEST_FAIL_KEY=binding',
        )
        self.assertEqual(result.returncode, 42)
        self.assertIn("cannot write custom shortcut binding", result.stderr)
        self.assertFalse((self.xdg / "ride-fedora/owned/setting.gnome-custom-shortcuts.json").exists())

    def test_invalid_shortcut_configuration_is_rejected(self):
        invalid = json.dumps({"global": {"showDesktop": [], "switchWindows": []},
                              "shortcuts": [{"name": "Bad'Name", "command": "x", "binding": "<Super>x"}]})
        entry = json.dumps({"id": "setting.gnome-custom-shortcuts"})
        result = self.shell(
            'ride_setting_value_valid "$TEST_ENTRY" "$TEST_VALUE"',
            extra='TEST_ENTRY=' + json.dumps(entry) + '\nTEST_VALUE=' + json.dumps(invalid),
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()

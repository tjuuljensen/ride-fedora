"""Typed, configurable GNOME favorite list validation and exact recovery."""

import base64
import json
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
CATALOG_MODULE = ROOT / "lib/v3/catalog.sh"


class GnomeFavoritesTests(unittest.TestCase):
    def shell(self, body, *, values=None):
        script = f"""set -euo pipefail
source {CATALOG_MODULE}
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_require_command() {{ :; }}
ride_gsettings() {{
  case "$1" in
    range) printf 'type as\\n' ;;
    writable) printf 'true\\n' ;;
    get) printf '%s\\n' "$TEST_EFFECTIVE" ;;
    set) TEST_EFFECTIVE=$4; TEST_OVERRIDE=$4; export TEST_EFFECTIVE TEST_OVERRIDE ;;
    reset) TEST_EFFECTIVE='[]'; TEST_OVERRIDE=; export TEST_EFFECTIVE TEST_OVERRIDE ;;
    *) printf 'unexpected gsettings call: %s\\n' "$*" >&2; return 2 ;;
  esac
}}
dconf() {{
  [[ "$1" == read ]] || return 2
  printf '%s\\n' "$TEST_OVERRIDE"
}}
{body}
"""
        env = os.environ.copy()
        env.update(values or {})
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_json_desktop_ids_convert_to_safe_gvariant_and_validate(self):
        selected = json.dumps(["firefox.desktop", "org.gnome.Nautilus.desktop"])
        entry = json.dumps({"id": "setting.gnome-favorite-apps"})
        result = self.shell(
            'ride_gsettings_favorite_variant "$TEST_VALUE"\n'
            'ride_setting_value_valid "$TEST_ENTRY" "$TEST_VALUE"',
            values={"TEST_ENTRY": entry, "TEST_VALUE": selected},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(),
                         ["['firefox.desktop', 'org.gnome.Nautilus.desktop']"])

    def test_invalid_or_duplicate_desktop_ids_are_rejected(self):
        entry = json.dumps({"id": "setting.gnome-favorite-apps"})
        for selected in ('["bad \' value.desktop"]',
                         '["duplicate.desktop","duplicate.desktop"]',
                         '["not-a-desktop-id"]',
                         json.dumps(["x" * 130 + ".desktop"]),
                         "[" + " " * 701 + "]"):
            with self.subTest(selected=selected):
                result = self.shell(
                    'ride_setting_value_valid "$TEST_ENTRY" "$TEST_VALUE"',
                    values={"TEST_ENTRY": entry, "TEST_VALUE": selected},
                )
                self.assertNotEqual(result.returncode, 0)

    def test_apply_and_restore_preserve_exact_prior_favorites(self):
        before = "['org.gnome.Nautilus.desktop']"
        selected = json.dumps(["firefox.desktop", "libreoffice-writer.desktop"])
        entry = json.dumps({"id": "setting.gnome-favorite-apps",
                            "selectedValue": selected,
                            "valueKind": "desktop-id-list"})
        result = self.shell(
            'before=$(ride_gsettings_string_observe "$TEST_ENTRY")\n'
            'ride_gsettings_string_change "$TEST_ENTRY" configured\n'
            'ride_gsettings_string_observe "$TEST_ENTRY"\n'
            'ride_gsettings_string_change "$TEST_ENTRY" "$before"\n'
            'ride_gsettings_string_observe "$TEST_ENTRY"',
            values={"TEST_ENTRY": entry, "TEST_EFFECTIVE": before, "TEST_OVERRIDE": before},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        encoded = "user:" + base64.b64encode(before.encode()).decode()
        self.assertEqual(result.stdout.splitlines(), ["configured", encoded])

    def test_absent_resets_the_selected_favorites_value(self):
        entry = json.dumps({"id": "setting.gnome-favorite-apps",
                            "selectedValue": json.dumps(["org.mozilla.firefox.desktop"]),
                            "valueKind": "desktop-id-list"})
        result = self.shell(
            'ride_gsettings_string_change "$TEST_ENTRY" absent\n'
            'ride_gsettings_string_observe "$TEST_ENTRY"',
            values={"TEST_ENTRY": entry,
                    "TEST_EFFECTIVE": "['org.gnome.Nautilus.desktop']",
                    "TEST_OVERRIDE": "['org.gnome.Nautilus.desktop']"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "absent")


if __name__ == "__main__":
    unittest.main()

"""GNOME lock timing presets write and restore all keys as one transaction."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ROOT / "lib/v3/providers.sh"


class GnomeLockTimingTests(unittest.TestCase):
    def run_provider(self, body, *, entry, state, overrides, fail_key=""):
        script = f'''set -euo pipefail
source {PROVIDERS}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_error() {{ printf '%s\\n' "$*" >&2; }}
ride_require_command() {{ :; }}
ENTRY={shlex.quote(json.dumps(entry))}
GNOME_STATE={shlex.quote(json.dumps(state, separators=(',', ':')))}
GNOME_OVERRIDES={shlex.quote(json.dumps(overrides, separators=(',', ':')))}
GNOME_FAIL_KEY={shlex.quote(fail_key)}
ride_gsettings() {{
  local op=$1 schema=$2 key=$3 value=${{4:-}}
  case "$op" in
    range) [[ "$key" == idle-delay || "$key" == lock-delay ]] && printf 'type u\\n' || printf 'type b\\n' ;;
    writable) printf 'true\\n' ;;
    get) jq -r --arg key "$key" '.[$key]' <<< "$GNOME_STATE" ;;
    set)
      if [[ "$key" == "$GNOME_FAIL_KEY" ]]; then GNOME_FAIL_KEY=; return 1; fi
      GNOME_STATE=$(jq -c --arg key "$key" --arg value "$value" '. + {{($key):$value}}' <<< "$GNOME_STATE")
      GNOME_OVERRIDES=$(jq -c --arg key "$key" --arg value "$value" '. + {{($key):$value}}' <<< "$GNOME_OVERRIDES") ;;
    reset)
      GNOME_STATE=$(jq -c --arg key "$key" '. + {{($key):""}}' <<< "$GNOME_STATE")
      GNOME_OVERRIDES=$(jq -c --arg key "$key" '. + {{($key):""}}' <<< "$GNOME_OVERRIDES") ;;
    *) return 2 ;;
  esac
}}
dconf() {{ local path=$2 key=${{path##*/}}; jq -r --arg key "$key" '.[$key] // ""' <<< "$GNOME_OVERRIDES"; }}
ride_gnome_lock_timing_paths() {{
  local selected
  selected=$(jq -r '.selectedValue // ""' <<< "$1")
  printf '%s\\n' \\
    'org.gnome.desktop.session idle-delay /org/gnome/desktop/session/idle-delay' \\
    'org.gnome.desktop.screensaver idle-activation-enabled /org/gnome/desktop/screensaver/idle-activation-enabled' \\
    'org.gnome.desktop.screensaver lock-enabled /org/gnome/desktop/screensaver/lock-enabled'
  [[ "$selected" == screensaver-enabled || "$selected" == screensaver-disabled ]] ||
    printf '%s\\n' 'org.gnome.desktop.screensaver lock-delay /org/gnome/desktop/screensaver/lock-delay'
}}
{body}
printf 'STATE=%s\\nOVERRIDES=%s\\n' "$GNOME_STATE" "$GNOME_OVERRIDES"
'''
        return subprocess.run(["bash", "-c", script], env=os.environ.copy(),
                              text=True, capture_output=True, check=False)

    def test_apply_repeat_and_exact_restore_of_four_values(self):
        initial = {"idle-delay": "uint32 720", "idle-activation-enabled": "false",
                   "lock-enabled": "false", "lock-delay": "uint32 40"}
        entry = {"id": "setting.gnome-lock-timing", "selectedValue": "idle-10-lock-5"}
        result = self.run_provider(
            'before=$(ride_gnome_lock_timing_observe "$ENTRY")\n'
            '[[ "$before" == prior:* ]]\n'
            'ride_gnome_lock_timing_change "$ENTRY" configured\n'
            '[[ "$(ride_gnome_lock_timing_observe "$ENTRY")" == configured ]]\n'
            'STATUS_ENTRY=\'{"id":"setting.gnome-lock-timing"}\'\n'
            '[[ "$(ride_gnome_lock_timing_observe "$STATUS_ENTRY")" == configured ]]\n'
            'ride_gnome_lock_timing_change "$ENTRY" "$before"\n'
            '[[ "$(ride_gnome_lock_timing_observe "$ENTRY")" == "$before" ]]',
            entry=entry, state=initial, overrides=initial)
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout.split("STATE=", 1)[1].splitlines()[0])
        self.assertEqual(state, initial)

    def test_partial_write_failure_restores_all_prior_overrides(self):
        initial = {"idle-delay": "uint32 720", "idle-activation-enabled": "false",
                   "lock-enabled": "false", "lock-delay": "uint32 40"}
        entry = {"id": "setting.gnome-lock-timing", "selectedValue": "idle-15-lock-5"}
        result = self.run_provider(
            'ride_gnome_lock_timing_change "$ENTRY" configured || rc=$?\n'
            '[[ ${rc:-0} == 1 ]]',
            entry=entry, state=initial, overrides=initial, fail_key="lock-enabled")
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout.split("STATE=", 1)[1].splitlines()[0])
        overrides = json.loads(result.stdout.split("OVERRIDES=", 1)[1].splitlines()[0])
        self.assertEqual(state, initial)
        self.assertEqual(overrides, initial)

    def test_legacy_enabled_and_disabled_states_preserve_lock_delay(self):
        initial = {"idle-delay": "uint32 720", "idle-activation-enabled": "false",
                   "lock-enabled": "false", "lock-delay": "uint32 40"}
        for selection, expected in (
            ("screensaver-enabled", {"idle-delay": "uint32 300",
                                      "idle-activation-enabled": "true",
                                      "lock-enabled": "true", "lock-delay": "uint32 40"}),
            ("screensaver-disabled", {"idle-delay": "uint32 0",
                                       "idle-activation-enabled": "false",
                                       "lock-enabled": "false", "lock-delay": "uint32 40"}),
        ):
            entry = {"id": "setting.gnome-lock-timing", "selectedValue": selection}
            result = self.run_provider(
                'before=$(ride_gnome_lock_timing_observe "$ENTRY")\n'
                'ride_gnome_lock_timing_change "$ENTRY" configured\n'
                '[[ "$(ride_gnome_lock_timing_observe "$ENTRY")" == configured ]]\n'
                + f'[[ "$(jq -r ".\\\"idle-delay\\\"" <<< "$GNOME_STATE")" == {shlex.quote(expected["idle-delay"])} ]]\n'
                + f'[[ "$(jq -r ".\\\"idle-activation-enabled\\\"" <<< "$GNOME_STATE")" == {shlex.quote(expected["idle-activation-enabled"])} ]]\n'
                + f'[[ "$(jq -r ".\\\"lock-enabled\\\"" <<< "$GNOME_STATE")" == {shlex.quote(expected["lock-enabled"])} ]]\n'
                '[[ "$(jq -r ".\\\"lock-delay\\\"" <<< "$GNOME_STATE")" == "uint32 40" ]]\n'
                'ride_gnome_lock_timing_change "$ENTRY" "$before"\n'
                '[[ "$(ride_gnome_lock_timing_observe "$ENTRY")" == "$before" ]]',
                entry=entry, state=initial, overrides=initial)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(result.stdout.split("STATE=", 1)[1].splitlines()[0])
            self.assertEqual(state, initial)
            # The mock lifecycle verifies the configured state before restore;
            # the lock-delay remains the seeded user value throughout apply.
            self.assertIn('"lock-delay":"uint32 40"', result.stdout)

    def test_snapshot_rejects_unknown_keys_and_untyped_values(self):
        entry = {"id": "setting.gnome-lock-timing", "selectedValue": "idle-10-lock-5"}
        result = self.run_provider(
            'ride_gnome_lock_timing_snapshot_valid "prior:eyJ1bnN1cHBvcnRlZCI6InRydWUifQ=="',
            entry=entry, state={"idle-delay": "uint32 720", "idle-activation-enabled": "false",
                                "lock-enabled": "false", "lock-delay": "uint32 40"},
            overrides={"idle-delay": "uint32 720", "idle-activation-enabled": "false",
                       "lock-enabled": "false", "lock-delay": "uint32 40"})
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()

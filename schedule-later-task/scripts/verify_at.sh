#!/usr/bin/env bash
set -euo pipefail

os="$(uname -s)"

if ! command -v at >/dev/null 2>&1; then
  echo "at utility not found"
  echo "Run: bash \"$(dirname "$0")/install_at.sh\""
  exit 2
fi

if at -l >/dev/null 2>&1; then
  echo "at utility is installed and responding"
  exit 0
fi

# Some systems return non-zero on empty queue; treat usage output as acceptable.
if at -V >/dev/null 2>&1 || at --version >/dev/null 2>&1; then
  echo "at utility is installed (version check passed)"
else
  echo "at utility found but usability could not be verified"
fi

case "$os" in
  Darwin)
    if command -v launchctl >/dev/null 2>&1; then
      if launchctl list 2>/dev/null | grep -q "com.apple.atrun"; then
        echo "atrun launchd job appears loaded"
      else
        echo "atrun launchd job not detected; scheduled jobs may not execute until loaded"
      fi
    fi
    ;;
  Linux)
    if command -v systemctl >/dev/null 2>&1; then
      if systemctl is-enabled atd >/dev/null 2>&1 || systemctl is-enabled atd.service >/dev/null 2>&1; then
        echo "atd service appears enabled"
      else
        echo "atd service not enabled; run install script or enable atd manually"
      fi
    fi
    ;;
esac

exit 0

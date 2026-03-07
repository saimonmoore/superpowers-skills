#!/usr/bin/env bash
set -euo pipefail

os="$(uname -s)"

install_macos() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required to install at on macOS"
    echo "Install Homebrew first: https://brew.sh"
    exit 1
  fi

  brew list at >/dev/null 2>&1 || brew install at

  if command -v launchctl >/dev/null 2>&1; then
    if [ -f /System/Library/LaunchDaemons/com.apple.atrun.plist ]; then
      echo "Attempting to load atrun launchd daemon (may require sudo)"
      sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist || true
    fi
  fi

  echo "macOS install flow complete"
}

install_linux() {
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y at
    sudo systemctl enable --now atd || true
    return
  fi

  if command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y at
    sudo systemctl enable --now atd || true
    return
  fi

  if command -v yum >/dev/null 2>&1; then
    sudo yum install -y at
    sudo systemctl enable --now atd || true
    return
  fi

  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm at
    sudo systemctl enable --now atd || true
    return
  fi

  if command -v zypper >/dev/null 2>&1; then
    sudo zypper --non-interactive install at
    sudo systemctl enable --now atd || true
    return
  fi

  if command -v apk >/dev/null 2>&1; then
    sudo apk add at
    rc-update add atd default || true
    rc-service atd start || true
    return
  fi

  echo "Unsupported Linux package manager; install 'at' manually"
  exit 1
}

case "$os" in
  Darwin)
    install_macos
    ;;
  Linux)
    install_linux
    ;;
  *)
    echo "Unsupported OS: $os"
    exit 1
    ;;
esac

echo "Verifying installation..."
bash "$(dirname "$0")/verify_at.sh"

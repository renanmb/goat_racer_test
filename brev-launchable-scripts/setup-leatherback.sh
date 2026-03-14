#!/usr/bin/env bash
set -euo pipefail

# setup-leatherback.sh (version 01)
# Installs the Leatherback project into the 'isaaclab' conda environment

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
TARGET_USER="ubuntu"
CONDA_ENV_NAME="isaaclab"
# Find the repository root (goat_racer_test) based on this script's location
REPO_ROOT="$(readlink -f "$(dirname "$0")")"
LEATHERBACK_DIR="$REPO_ROOT/leatherback"

log() { echo -e "\n>>> [Leatherback Setup] $*"; }
fail() { echo -e "\n❌ [ERROR] $*" >&2; exit 1; }

# -----------------------------------------------------------------------------
# Pre-checks
# -----------------------------------------------------------------------------
if [[ "$EUID" -ne 0 ]]; then
  fail "This script must be run as root (sudo)"
fi

if [[ ! -d "$LEATHERBACK_DIR" ]]; then
  fail "Leatherback directory not found at: $LEATHERBACK_DIR"
fi

# -----------------------------------------------------------------------------
# Installation
# -----------------------------------------------------------------------------
log "Installing Leatherback into environment: $CONDA_ENV_NAME"

# We use -i (login shell) and -u (target user) to ensure PATHs are loaded correctly.
# 'conda run' executes the command within the specific environment context.
sudo -H -u "$TARGET_USER" -i \
    conda run -n "$CONDA_ENV_NAME" \
    --cwd "$LEATHERBACK_DIR" \
    python -m pip install -e source/leatherback

# -----------------------------------------------------------------------------
# Verification
# -----------------------------------------------------------------------------
log "Verifying installation..."

if sudo -H -u "$TARGET_USER" -i conda run -n "$CONDA_ENV_NAME" python -c "import leatherback; print('Leatherback successfully imported!')" ; then
    log "✅ Leatherback setup completed successfully."
else
    fail "Verification failed. Leatherback module not found in '$CONDA_ENV_NAME'."
fi
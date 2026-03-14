#!/usr/bin/env bash
set -euo pipefail

############################
# CONFIG
############################
ANSIBLE_USER="ubuntu"
HOME_DIR="/home/${ANSIBLE_USER}"
CONDA_ENV_NAME="isaaclab"
PROJECT_VERSION="dataset-handler"

log() { echo -e "\n>>> $*\n"; }

############################
# PRE-REQUISITES (APT)
############################
log "Installing system dependencies"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git \
    curl \
    cmake \
    build-essential

############################
# LEATHERBACK SETUP 
############################
log "Cloning LeIsaac (${LEISAAC_VERSION})"
if [ ! -d "$HOME_DIR/leisaac" ]; then
    sudo -u "$ANSIBLE_USER" git clone --recursive https://github.com/renanmb/leisaac.git "$HOME_DIR/leisaac"
    cd "$HOME_DIR/leisaac"
    sudo -u "$ANSIBLE_USER" git checkout "$LEISAAC_VERSION"
fi

############################
# INSTALLATION
############################
log "Installing LeIsaac and GR00T dependencies"

# Using 'conda run' ensures we are in the correct env context without needing to 'source' conda.sh
sudo -u "$ANSIBLE_USER" -i conda run -n "$CONDA_ENV_NAME" --cwd "$HOME_DIR/leisaac" \
    pip install -e source/leisaac

log "Installing optional GR00T dependencies"
sudo -u "$ANSIBLE_USER" -i conda run -n "$CONDA_ENV_NAME" --cwd "$HOME_DIR/leisaac" \
    pip install -e "source/leisaac[gr00t]"


# 5. Build extensions
echo "▶ Building extensions (This may take 10+ minutes)..."
# Force the use of the conda-specific python for the install
conda run -n "$CONDA_ENV_NAME" ./isaaclab.sh -i

############################
# VERIFICATION
############################
log "Verifying installation"
sudo -u "$ANSIBLE_USER" -i conda run -n "$CONDA_ENV_NAME" isaaclab -i

log "LeIsaac setup completed successfully."
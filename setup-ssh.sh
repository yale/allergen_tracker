#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/.env.deploy" ]; then
  source "$SCRIPT_DIR/.env.deploy"
else
  echo "Error: .env.deploy not found. Copy .env.deploy.example to .env.deploy and fill in your values."
  exit 1
fi

echo "Setting up passwordless SSH to ${NAS_USER}@${NAS_HOST}..."

# Copy SSH key
ssh-copy-id "${NAS_USER}@${NAS_HOST}"

echo ""
echo "SSH key copied! Now you need to configure passwordless sudo on the NAS."
echo ""
echo "Run the following commands on your NAS (you'll be prompted for password):"
echo ""
echo "  ssh ${NAS_USER}@${NAS_HOST}"
echo "  sudo visudo"
echo ""
echo "Add this line at the end:"
echo "  ${NAS_USER} ALL=(ALL) NOPASSWD: /usr/local/bin/docker-compose, /usr/bin/docker"
echo ""
echo "Save and exit (Ctrl+X, then Y, then Enter)"

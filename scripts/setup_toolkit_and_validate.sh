#!/usr/bin/env bash
# Automates submodule sync, Echo-Community-Toolkit setup, soulcode bundle generation,
# and final validator run for the Vessel Narrative MRP repository.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLKIT_DIR="${ROOT_DIR}/Echo-Community-Toolkit"

log() {
  printf '\n==> %s\n' "$1"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: '$1' is required but not installed." >&2
    exit 1
  fi
}

require_cmd git
require_cmd npm
require_cmd python

if [ ! -d "${TOOLKIT_DIR}" ]; then
  echo "Error: Echo-Community-Toolkit submodule not found at ${TOOLKIT_DIR}" >&2
  echo "Run from repository root after cloning with --recurse-submodules." >&2
  exit 1
fi

log "Synchronizing git submodules"
git -C "${ROOT_DIR}" submodule update --init --recursive

log "Updating Echo-Community-Toolkit to latest main"
git -C "${TOOLKIT_DIR}" fetch origin --tags
git -C "${TOOLKIT_DIR}" checkout main
git -C "${TOOLKIT_DIR}" pull --ff-only origin main

log "Installing toolkit dependencies"
(cd "${TOOLKIT_DIR}" && npm ci)

log "Generating soulcode artifacts"
(cd "${TOOLKIT_DIR}" && npm run soulcode:emit-schema)
(cd "${TOOLKIT_DIR}" && npm run soulcode:bundle)
(cd "${TOOLKIT_DIR}" && npm run soulcode:validate)

log "Embedding soulcode bundle into narrative (optional HyperFollow integration)"
SOULCODE_BUNDLE_PATH="${TOOLKIT_DIR}/integration/outputs/echo_live.json"
if [ -f "${SOULCODE_BUNDLE_PATH}" ]; then
  (cd "${TOOLKIT_DIR}" && SOULCODE_BUNDLE="${SOULCODE_BUNDLE_PATH}" npm run integrate)
else
  echo "Warning: Soulcode bundle not found at ${SOULCODE_BUNDLE_PATH}. Skipping integrate step." >&2
fi

log "Verifying toolkit integration"
(cd "${TOOLKIT_DIR}" && npm run verify || echo "HyperFollow verification reported issues.")

log "Running Vessel Narrative validator"
(cd "${ROOT_DIR}" && python src/validator.py)

log "Completed toolkit setup and validation."

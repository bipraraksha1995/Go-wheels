#!/usr/bin/env bash
set -euo pipefail

echo "🔎 Generating SBOM for GoWheels"

if ! command -v syft >/dev/null 2>&1; then
  echo "syft not found — installing..."
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
fi

echo "Running syft to produce CycloneDX JSON sbom.json"
syft . -o cyclonedx-json=sbom.json

echo "SBOM generated: ./sbom.json"

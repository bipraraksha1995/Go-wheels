@echo off
REM Generate SBOM for GoWheels (Windows)

where syft >nul 2>&1
if errorlevel 1 (
  echo syft not found. Please install syft manually from https://github.com/anchore/syft
  exit /b 1
)

echo Generating sbom.json with syft
syft . -o cyclonedx-json=sbom.json
echo SBOM generated: %cd%\sbom.json

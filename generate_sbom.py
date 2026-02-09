#!/usr/bin/env python
"""
SBOM (Software Bill of Materials) Generator
Generates SBOM in CycloneDX and SPDX formats
"""
import subprocess
import json
import datetime
import sys
from pathlib import Path


def generate_cyclonedx_sbom():
    """Generate SBOM in CycloneDX format"""
    print("Generating CycloneDX SBOM...")
    
    try:
        result = subprocess.run(
            ['cyclonedx-py', '-r', '-o', 'sbom-cyclonedx.json'],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ CycloneDX SBOM generated: sbom-cyclonedx.json")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating CycloneDX SBOM: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  cyclonedx-py not installed. Run: pip install cyclonedx-bom")
        return False


def generate_spdx_sbom():
    """Generate SBOM in SPDX format"""
    print("Generating SPDX SBOM...")
    
    try:
        # Get package list
        result = subprocess.run(
            ['pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        
        # Create SPDX document
        spdx_doc = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "GoWheels-SBOM",
            "documentNamespace": f"https://gowheels.com/sbom/{datetime.datetime.now().isoformat()}",
            "creationInfo": {
                "created": datetime.datetime.now().isoformat(),
                "creators": ["Tool: GoWheels-SBOM-Generator"],
                "licenseListVersion": "3.21"
            },
            "packages": []
        }
        
        # Add packages
        for pkg in packages:
            package = {
                "SPDXID": f"SPDXRef-Package-{pkg['name']}",
                "name": pkg['name'],
                "versionInfo": pkg['version'],
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION"
            }
            spdx_doc["packages"].append(package)
        
        # Write SPDX file
        with open('sbom-spdx.json', 'w') as f:
            json.dump(spdx_doc, f, indent=2)
        
        print("✅ SPDX SBOM generated: sbom-spdx.json")
        return True
    except Exception as e:
        print(f"❌ Error generating SPDX SBOM: {e}")
        return False


def generate_simple_sbom():
    """Generate simple human-readable SBOM"""
    print("Generating simple SBOM...")
    
    try:
        # Get package list with licenses
        result = subprocess.run(
            ['pip-licenses', '--format=json', '--with-urls'],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        
        # Create markdown SBOM
        sbom_md = f"""# GoWheels Software Bill of Materials (SBOM)

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** GoWheels  
**Version:** 1.0.0  
**Total Dependencies:** {len(packages)}

## Dependencies

| Package | Version | License | URL |
|---------|---------|---------|-----|
"""
        
        for pkg in sorted(packages, key=lambda x: x['Name'].lower()):
            name = pkg.get('Name', 'Unknown')
            version = pkg.get('Version', 'Unknown')
            license_name = pkg.get('License', 'UNKNOWN')
            url = pkg.get('URL', 'N/A')
            
            sbom_md += f"| {name} | {version} | {license_name} | {url} |\n"
        
        sbom_md += f"""
## License Summary

- **Permissive Licenses:** MIT, Apache-2.0, BSD
- **Copyleft Licenses:** GPL, LGPL (if any)
- **Unknown Licenses:** Require manual review

## Compliance

This SBOM is generated automatically and should be reviewed for:
1. License compatibility
2. Security vulnerabilities
3. Outdated dependencies
4. Legal compliance

## Contact

For questions about this SBOM, contact: legal@gowheels.com
"""
        
        with open('SBOM.md', 'w') as f:
            f.write(sbom_md)
        
        print("✅ Simple SBOM generated: SBOM.md")
        return True
    except Exception as e:
        print(f"❌ Error generating simple SBOM: {e}")
        return False


def generate_requirements_lock():
    """Generate locked requirements file"""
    print("Generating requirements.lock...")
    
    try:
        result = subprocess.run(
            ['pip', 'freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        
        with open('requirements.lock', 'w') as f:
            f.write(f"# Generated: {datetime.datetime.now().isoformat()}\n")
            f.write(f"# Python version: {sys.version.split()[0]}\n\n")
            f.write(result.stdout)
        
        print("✅ Requirements lock generated: requirements.lock")
        return True
    except Exception as e:
        print(f"❌ Error generating requirements.lock: {e}")
        return False


def main():
    print("=" * 70)
    print("GoWheels SBOM Generator")
    print("=" * 70)
    print()
    
    results = []
    
    # Generate all SBOM formats
    results.append(("CycloneDX", generate_cyclonedx_sbom()))
    results.append(("SPDX", generate_spdx_sbom()))
    results.append(("Simple", generate_simple_sbom()))
    results.append(("Requirements Lock", generate_requirements_lock()))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\nGenerated {successful}/{len(results)} SBOM files")
    
    if successful > 0:
        print("\n📄 Generated files:")
        if Path('sbom-cyclonedx.json').exists():
            print("  - sbom-cyclonedx.json (CycloneDX format)")
        if Path('sbom-spdx.json').exists():
            print("  - sbom-spdx.json (SPDX format)")
        if Path('SBOM.md').exists():
            print("  - SBOM.md (Human-readable)")
        if Path('requirements.lock').exists():
            print("  - requirements.lock (Locked dependencies)")


if __name__ == '__main__':
    main()

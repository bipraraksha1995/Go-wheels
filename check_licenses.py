#!/usr/bin/env python
"""
Dependency License Checker
Scans all dependencies for license compliance
"""
import subprocess
import json
import sys
from collections import defaultdict

# Approved licenses (permissive)
APPROVED_LICENSES = {
    'MIT',
    'Apache-2.0',
    'Apache Software License',
    'BSD',
    'BSD-3-Clause',
    'BSD-2-Clause',
    'ISC',
    'Python Software Foundation License',
    'PSF',
    'Mozilla Public License 2.0 (MPL 2.0)',
    'MPL-2.0',
}

# Restricted licenses (copyleft - requires review)
RESTRICTED_LICENSES = {
    'GPL',
    'GPLv2',
    'GPLv3',
    'LGPL',
    'LGPLv2',
    'LGPLv3',
    'AGPL',
    'AGPLv3',
}

# Forbidden licenses
FORBIDDEN_LICENSES = {
    'UNKNOWN',
    'Proprietary',
}


def get_installed_packages():
    """Get list of installed packages with licenses"""
    try:
        result = subprocess.run(
            ['pip-licenses', '--format=json', '--with-urls'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        print("Error: pip-licenses not installed. Run: pip install pip-licenses")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Failed to parse license data")
        sys.exit(1)


def check_license(license_name):
    """Check if license is approved, restricted, or forbidden"""
    if not license_name or license_name == 'UNKNOWN':
        return 'FORBIDDEN', 'Unknown license'
    
    # Normalize license name
    license_upper = license_name.upper()
    
    # Check approved
    for approved in APPROVED_LICENSES:
        if approved.upper() in license_upper:
            return 'APPROVED', 'Permissive license'
    
    # Check restricted
    for restricted in RESTRICTED_LICENSES:
        if restricted.upper() in license_upper:
            return 'RESTRICTED', 'Copyleft license - requires review'
    
    # Check forbidden
    for forbidden in FORBIDDEN_LICENSES:
        if forbidden.upper() in license_upper:
            return 'FORBIDDEN', 'Forbidden license'
    
    return 'UNKNOWN', 'License not in approved list - requires review'


def main():
    print("=" * 70)
    print("GoWheels Dependency License Check")
    print("=" * 70)
    
    packages = get_installed_packages()
    
    # Categorize packages
    approved = []
    restricted = []
    forbidden = []
    unknown = []
    
    for pkg in packages:
        name = pkg.get('Name', 'Unknown')
        version = pkg.get('Version', 'Unknown')
        license_name = pkg.get('License', 'UNKNOWN')
        url = pkg.get('URL', '')
        
        status, reason = check_license(license_name)
        
        pkg_info = {
            'name': name,
            'version': version,
            'license': license_name,
            'url': url,
            'reason': reason
        }
        
        if status == 'APPROVED':
            approved.append(pkg_info)
        elif status == 'RESTRICTED':
            restricted.append(pkg_info)
        elif status == 'FORBIDDEN':
            forbidden.append(pkg_info)
        else:
            unknown.append(pkg_info)
    
    # Print results
    print(f"\n✅ APPROVED ({len(approved)} packages)")
    print("-" * 70)
    for pkg in approved[:5]:  # Show first 5
        print(f"  {pkg['name']} {pkg['version']} - {pkg['license']}")
    if len(approved) > 5:
        print(f"  ... and {len(approved) - 5} more")
    
    if restricted:
        print(f"\n⚠️  RESTRICTED ({len(restricted)} packages) - REQUIRES REVIEW")
        print("-" * 70)
        for pkg in restricted:
            print(f"  {pkg['name']} {pkg['version']} - {pkg['license']}")
            print(f"     Reason: {pkg['reason']}")
    
    if forbidden:
        print(f"\n❌ FORBIDDEN ({len(forbidden)} packages) - MUST REMOVE")
        print("-" * 70)
        for pkg in forbidden:
            print(f"  {pkg['name']} {pkg['version']} - {pkg['license']}")
            print(f"     Reason: {pkg['reason']}")
    
    if unknown:
        print(f"\n❓ UNKNOWN ({len(unknown)} packages) - REQUIRES REVIEW")
        print("-" * 70)
        for pkg in unknown:
            print(f"  {pkg['name']} {pkg['version']} - {pkg['license']}")
            print(f"     URL: {pkg['url']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total packages: {len(packages)}")
    print(f"✅ Approved: {len(approved)}")
    print(f"⚠️  Restricted: {len(restricted)}")
    print(f"❌ Forbidden: {len(forbidden)}")
    print(f"❓ Unknown: {len(unknown)}")
    
    # Exit code
    if forbidden:
        print("\n❌ FAILED: Forbidden licenses detected")
        sys.exit(1)
    elif restricted or unknown:
        print("\n⚠️  WARNING: Restricted/Unknown licenses require review")
        sys.exit(0)
    else:
        print("\n✅ PASSED: All licenses approved")
        sys.exit(0)


if __name__ == '__main__':
    main()

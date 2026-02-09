#!/usr/bin/env python
"""
Automated Code Cleanup
Removes unused imports, formats code, removes dead code
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run shell command"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout:
                print(result.stdout[:500])
        else:
            print(f"⚠️  {description} had warnings")
            if result.stderr:
                print(result.stderr[:500])
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("=" * 70)
    print("GoWheels Automated Code Cleanup")
    print("=" * 70)
    
    # Check if tools are installed
    tools = {
        'autoflake': 'pip install autoflake',
        'isort': 'pip install isort',
        'black': 'pip install black',
        'pylint': 'pip install pylint',
    }
    
    print("\n📦 Checking required tools...")
    missing_tools = []
    for tool, install_cmd in tools.items():
        result = subprocess.run(f"{tool} --version", shell=True, capture_output=True)
        if result.returncode != 0:
            missing_tools.append((tool, install_cmd))
            print(f"  ❌ {tool} not installed")
        else:
            print(f"  ✅ {tool} installed")
    
    if missing_tools:
        print("\n⚠️  Missing tools. Install with:")
        for tool, cmd in missing_tools:
            print(f"  {cmd}")
        sys.exit(1)
    
    # Cleanup steps
    steps = [
        # Remove unused imports
        ("autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive gowheels/",
         "Removing unused imports"),
        
        # Sort imports
        ("isort gowheels/ gowheels_project/",
         "Sorting imports"),
        
        # Format code
        ("black gowheels/ gowheels_project/",
         "Formatting code with Black"),
        
        # Remove trailing whitespace
        ("find gowheels/ -name '*.py' -exec sed -i 's/[ \t]*$//' {} +",
         "Removing trailing whitespace"),
    ]
    
    results = []
    for cmd, description in steps:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\nCompleted {successful}/{len(results)} cleanup tasks")
    
    print("\n💡 Next steps:")
    print("  1. Review changes: git diff")
    print("  2. Run tests: python manage.py test")
    print("  3. Commit changes: git commit -am 'Clean up unused code'")

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
Unused Code Detector
Finds unused files, imports, functions, and variables
"""
import os
import ast
import re
from pathlib import Path
from collections import defaultdict

# Directories to scan
SCAN_DIRS = ['gowheels', 'gowheels_project']
EXCLUDE_DIRS = {'__pycache__', 'migrations', '.git', 'venv', 'env', 'staticfiles', 'media'}
EXCLUDE_FILES = {'__init__.py', 'manage.py', 'wsgi.py', 'asgi.py'}


class UnusedCodeDetector:
    """Detect unused code in Python files"""
    
    def __init__(self):
        self.all_files = []
        self.imports = defaultdict(list)
        self.functions = defaultdict(list)
        self.classes = defaultdict(list)
        self.variables = defaultdict(list)
        self.usage = defaultdict(int)
    
    def scan_directory(self, directory):
        """Scan directory for Python files"""
        for root, dirs, files in os.walk(directory):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith('.py') and file not in EXCLUDE_FILES:
                    filepath = os.path.join(root, file)
                    self.all_files.append(filepath)
    
    def analyze_file(self, filepath):
        """Analyze Python file for definitions and usage"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filepath)
            
            # Find definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.functions[filepath].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    self.classes[filepath].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[filepath].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            self.imports[filepath].append(f"{node.module}.{alias.name}")
            
            # Count usage
            for name in self.functions[filepath] + self.classes[filepath]:
                # Simple regex search for usage
                pattern = rf'\b{re.escape(name)}\b'
                matches = len(re.findall(pattern, content))
                self.usage[name] += matches
        
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
    
    def find_unused_imports(self, filepath):
        """Find unused imports in a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            unused = []
            for imp in self.imports[filepath]:
                # Extract module/function name
                parts = imp.split('.')
                name = parts[-1]
                
                # Check if used (simple check)
                if content.count(name) <= 1:  # Only appears in import
                    unused.append(imp)
            
            return unused
        except:
            return []
    
    def find_unused_functions(self):
        """Find functions that are never called"""
        unused = []
        
        for filepath, functions in self.functions.items():
            for func in functions:
                # Skip special methods
                if func.startswith('__') and func.endswith('__'):
                    continue
                
                # Check if used only once (definition)
                if self.usage.get(func, 0) <= 1:
                    unused.append((filepath, func))
        
        return unused
    
    def find_unused_files(self):
        """Find Python files that are never imported"""
        unused = []
        
        for filepath in self.all_files:
            filename = os.path.basename(filepath)
            module_name = filename.replace('.py', '')
            
            # Check if module is imported anywhere
            is_imported = False
            for imports in self.imports.values():
                if any(module_name in imp for imp in imports):
                    is_imported = True
                    break
            
            # Check if it's a view/URL file (likely used)
            if 'views.py' in filename or 'urls.py' in filename:
                continue
            
            if not is_imported:
                unused.append(filepath)
        
        return unused


def find_empty_files():
    """Find empty or nearly empty Python files"""
    empty_files = []
    
    for directory in SCAN_DIRS:
        if not os.path.exists(directory):
            continue
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        # Check if empty or only comments/docstrings
                        lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
                        
                        if len(lines) <= 3:  # Very small file
                            empty_files.append((filepath, len(lines)))
                    except:
                        pass
    
    return empty_files


def find_duplicate_code():
    """Find duplicate code blocks"""
    # Simple duplicate detection
    code_blocks = defaultdict(list)
    
    for directory in SCAN_DIRS:
        if not os.path.exists(directory):
            continue
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Split into functions
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                func_code = ast.get_source_segment(content, node)
                                if func_code and len(func_code) > 100:
                                    code_blocks[func_code].append((filepath, node.name))
                    except:
                        pass
    
    duplicates = {code: files for code, files in code_blocks.items() if len(files) > 1}
    return duplicates


def main():
    print("=" * 70)
    print("GoWheels Unused Code Detector")
    print("=" * 70)
    
    detector = UnusedCodeDetector()
    
    # Scan all directories
    print("\n📁 Scanning directories...")
    for directory in SCAN_DIRS:
        if os.path.exists(directory):
            detector.scan_directory(directory)
            print(f"  Found {len(detector.all_files)} Python files in {directory}/")
    
    # Analyze files
    print("\n🔍 Analyzing files...")
    for filepath in detector.all_files:
        detector.analyze_file(filepath)
    
    # Find unused imports
    print("\n📦 Unused Imports:")
    print("-" * 70)
    unused_imports_count = 0
    for filepath in detector.all_files:
        unused = detector.find_unused_imports(filepath)
        if unused:
            print(f"\n{filepath}:")
            for imp in unused[:5]:  # Show first 5
                print(f"  - {imp}")
            if len(unused) > 5:
                print(f"  ... and {len(unused) - 5} more")
            unused_imports_count += len(unused)
    
    if unused_imports_count == 0:
        print("  ✅ No unused imports found")
    else:
        print(f"\n  Total: {unused_imports_count} unused imports")
    
    # Find unused functions
    print("\n🔧 Unused Functions:")
    print("-" * 70)
    unused_functions = detector.find_unused_functions()
    if unused_functions:
        for filepath, func in unused_functions[:10]:  # Show first 10
            print(f"  {filepath}: {func}()")
        if len(unused_functions) > 10:
            print(f"  ... and {len(unused_functions) - 10} more")
        print(f"\n  Total: {len(unused_functions)} unused functions")
    else:
        print("  ✅ No unused functions found")
    
    # Find unused files
    print("\n📄 Potentially Unused Files:")
    print("-" * 70)
    unused_files = detector.find_unused_files()
    if unused_files:
        for filepath in unused_files[:10]:
            print(f"  {filepath}")
        if len(unused_files) > 10:
            print(f"  ... and {len(unused_files) - 10} more")
        print(f"\n  Total: {len(unused_files)} potentially unused files")
    else:
        print("  ✅ No unused files found")
    
    # Find empty files
    print("\n📭 Empty/Small Files:")
    print("-" * 70)
    empty_files = find_empty_files()
    if empty_files:
        for filepath, lines in empty_files:
            print(f"  {filepath} ({lines} lines)")
        print(f"\n  Total: {len(empty_files)} empty/small files")
    else:
        print("  ✅ No empty files found")
    
    # Find duplicates
    print("\n🔄 Duplicate Code:")
    print("-" * 70)
    duplicates = find_duplicate_code()
    if duplicates:
        for i, (code, files) in enumerate(list(duplicates.items())[:3]):
            print(f"\n  Duplicate #{i+1}:")
            for filepath, func in files:
                print(f"    {filepath}: {func}()")
        if len(duplicates) > 3:
            print(f"\n  ... and {len(duplicates) - 3} more duplicates")
        print(f"\n  Total: {len(duplicates)} duplicate code blocks")
    else:
        print("  ✅ No duplicate code found")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files scanned: {len(detector.all_files)}")
    print(f"Unused imports: {unused_imports_count}")
    print(f"Unused functions: {len(unused_functions)}")
    print(f"Unused files: {len(unused_files)}")
    print(f"Empty files: {len(empty_files)}")
    print(f"Duplicate blocks: {len(duplicates)}")
    
    print("\n💡 Recommendations:")
    if unused_imports_count > 0:
        print("  - Remove unused imports with: autoflake --remove-all-unused-imports -i file.py")
    if unused_functions:
        print("  - Review unused functions - they may be dead code")
    if empty_files:
        print("  - Consider removing empty files")
    if duplicates:
        print("  - Refactor duplicate code into shared functions")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
File Size Monitor - Check all Python files for adherence to 300-line limit (project files only)
"""
import os
import sys
from pathlib import Path

def check_file_sizes(root_dir, max_lines=300):
    """Check all Python files in the project for size compliance"""
    violations = []
    compliant = []
    
    # Walk through all Python files
    for py_file in Path(root_dir).rglob("*.py"):
        # Skip archived files, venv, node_modules, and __pycache__
        if any(skip_dir in str(py_file) for skip_dir in [
            "__pycache__", "/archive/", "/venv/", "/node_modules/", "/.git/"
        ]):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            relative_path = os.path.relpath(py_file, root_dir)
            
            if line_count > max_lines:
                violations.append((relative_path, line_count))
            else:
                compliant.append((relative_path, line_count))
        except Exception as e:
            print(f"⚠️  Error reading {py_file}: {e}")
    
    return violations, compliant

def main():
    project_root = "/home/ammar/claude_projects/bank_statement_parser"
    max_lines = 300
    
    print(f"🔍 Checking Python file sizes in: {project_root}")
    print(f"📏 Maximum allowed lines: {max_lines}")
    print("=" * 80)
    
    violations, compliant = check_file_sizes(project_root, max_lines)
    
    if violations:
        print(f"\n❌ PROJECT FILES EXCEEDING {max_lines} LINES:")
        violations.sort(key=lambda x: x[1], reverse=True)  # Sort by line count
        for file_path, line_count in violations:
            percent_over = ((line_count - max_lines) / max_lines) * 100
            print(f"   {file_path}: {line_count} lines ({percent_over:.1f}% over limit)")
    else:
        print(f"\n✅ ALL PROJECT FILES UNDER {max_lines} LINES!")
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Compliant files: {len(compliant)}")
    print(f"   ❌ Violations: {len(violations)}")
    
    # Show largest compliant files (close to limit)
    large_compliant = [(f, c) for f, c in compliant if c > max_lines * 0.8]
    if large_compliant:
        print(f"\n⚠️  FILES CLOSE TO LIMIT (>{max_lines * 0.8:.0f} lines):")
        large_compliant.sort(key=lambda x: x[1], reverse=True)
        for file_path, line_count in large_compliant[:10]:
            print(f"   {file_path}: {line_count} lines")
    
    return len(violations) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

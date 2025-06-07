#!/usr/bin/env python3
"""
Audit script to check the line count of all Python files in the project.
Helps identify files that need refactoring (>300 lines).
"""

import os
import glob
from pathlib import Path

def count_lines_in_file(filepath):
    """Count lines in a file, handling encoding issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return len(f.readlines())
        except Exception as e:
            return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def audit_python_files(root_dir):
    """Audit all Python files in the project."""
    python_files = []
    
    # Find all .py files recursively
    for filepath in Path(root_dir).rglob('*.py'):
        if '__pycache__' in str(filepath) or 'venv' in str(filepath):
            continue
            
        line_count = count_lines_in_file(filepath)
        relative_path = filepath.relative_to(root_dir)
        python_files.append((str(relative_path), line_count))
    
    # Sort by line count (descending)
    python_files.sort(key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True)
    
    print("=" * 80)
    print("PYTHON FILE LENGTH AUDIT")
    print("=" * 80)
    print(f"{'File Path':<60} {'Lines':<10}")
    print("-" * 70)
    
    files_over_300 = []
    total_files = 0
    total_lines = 0
    
    for filepath, line_count in python_files:
        if isinstance(line_count, int):
            status = "⚠️  NEEDS REFACTOR" if line_count > 300 else "✅"
            print(f"{filepath:<60} {line_count:<10} {status}")
            
            if line_count > 300:
                files_over_300.append((filepath, line_count))
            
            total_files += 1
            total_lines += line_count
        else:
            print(f"{filepath:<60} {str(line_count):<10}")
    
    print("-" * 70)
    print(f"Total Python files: {total_files}")
    print(f"Total lines of code: {total_lines}")
    print(f"Average lines per file: {total_lines // total_files if total_files > 0 else 0}")
    
    if files_over_300:
        print("\n" + "=" * 80)
        print("FILES REQUIRING REFACTORING (>300 lines):")
        print("=" * 80)
        for filepath, line_count in files_over_300:
            print(f"🔴 {filepath}: {line_count} lines")
        
        print(f"\nRefactoring priority: {len(files_over_300)} files need attention")
    else:
        print("\n🎉 All files are under 300 lines!")

if __name__ == "__main__":
    project_root = "/home/ammar/claude_projects/bank_statement_parser"
    audit_python_files(project_root)

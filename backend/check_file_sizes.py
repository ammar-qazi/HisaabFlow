#!/usr/bin/env python3
"""
File Size Monitor - Ensures main.py stays under 300 lines
Run this script to check if main files are getting too large
"""

import os
import sys

# Define file size limits
SIZE_LIMITS = {
    'main.py': 300,  # Clean modular version
    'main_legacy.py': 0,  # Should remain archived (legacy bloated version)
    'data_cleaner.py': 300,
    'enhanced_csv_parser.py': 600,  # Allowed to be larger but monitored
    'transfer_detector_enhanced_ammar.py': 0,  # Should be archived (0 = archived)
}

def check_file_sizes():
    """Check if critical files are within size limits"""
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    results = []
    
    print("📏 File Size Monitor - Checking Critical Files")
    print("=" * 50)
    
    for filename, limit in SIZE_LIMITS.items():
        filepath = os.path.join(backend_dir, filename)
        
        if not os.path.exists(filepath):
            if limit == 0:  # Expected to be archived
                print(f"✅ {filename}: Properly archived (not found)")
                results.append(('archived', filename, 0, limit))
            else:
                print(f"⚠️  {filename}: File not found")
                results.append(('missing', filename, 0, limit))
            continue
        
        # Count lines
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for _ in f)
        
        if limit == 0:  # Should be archived
            print(f"❌ {filename}: {line_count} lines (SHOULD BE ARCHIVED)")
            results.append(('should_archive', filename, line_count, limit))
        elif line_count <= limit:
            print(f"✅ {filename}: {line_count}/{limit} lines (OK)")
            results.append(('ok', filename, line_count, limit))
        elif line_count <= limit * 1.1:  # Within 10% tolerance
            print(f"⚠️  {filename}: {line_count}/{limit} lines (WARNING - Close to limit)")
            results.append(('warning', filename, line_count, limit))
        else:
            print(f"❌ {filename}: {line_count}/{limit} lines (EXCEEDS LIMIT)")
            results.append(('exceed', filename, line_count, limit))
    
    print("\n📊 Summary:")
    
    issues = [r for r in results if r[0] in ['exceed', 'should_archive', 'warning']]
    
    if not issues:
        print("✅ All files are within acceptable size limits!")
        return True
    else:
        print(f"⚠️  Found {len(issues)} files that need attention:")
        for status, filename, lines, limit in issues:
            if status == 'exceed':
                print(f"   📏 {filename}: {lines} lines > {limit} limit - NEEDS REFACTORING")
            elif status == 'should_archive':
                print(f"   📦 {filename}: {lines} lines - SHOULD BE ARCHIVED")
            elif status == 'warning':
                print(f"   ⚠️  {filename}: {lines} lines - CLOSE TO {limit} LIMIT")
        
        print(f"\n🔧 Recommended Actions:")
        for status, filename, lines, limit in issues:
            if status == 'exceed':
                print(f"   • Refactor {filename} into smaller modules")
            elif status == 'should_archive':
                print(f"   • Move {filename} to archive/ directory")
            elif status == 'warning':
                print(f"   • Monitor {filename} for further growth")
        
        return False

def suggest_refactoring_for_file(filename, lines):
    """Suggest refactoring strategies for oversized files"""
    
    print(f"\n🔧 Refactoring Suggestions for {filename} ({lines} lines):")
    
    if filename == 'main.py':
        print("   • Move endpoint implementations to api/ modules")
        print("   • Extract complex logic into service classes")
        print("   • Use FastAPI router inclusion instead of inline endpoints")
        print("   • Move middleware and models to separate files")
        print("   • Consider using dependency injection for common components")
    
    elif filename.endswith('_parser.py'):
        print("   • Split parsing logic by data type (CSV, Excel, etc.)")
        print("   • Extract validation logic to separate validator classes")
        print("   • Move format-specific parsers to sub-modules")
        print("   • Create parser factory pattern")
    
    elif filename.endswith('_cleaner.py'):
        print("   • Split by cleaning operation type (dates, currency, text, etc.)")
        print("   • Extract rules and configurations to separate files")
        print("   • Create cleaner pipeline pattern")
        print("   • Move validation logic to separate validator")
    
    else:
        print("   • Look for large functions that can be split")
        print("   • Extract utility functions to separate modules")
        print("   • Consider using composition over inheritance")
        print("   • Move constants and configurations to separate files")

if __name__ == "__main__":
    print("🎯 Running file size check...\n")
    
    success = check_file_sizes()
    
    if not success:
        print(f"\n⚠️  Action Required: Some files exceed size limits!")
        print(f"   Run this script regularly to monitor file growth")
        sys.exit(1)
    else:
        print(f"\n🎉 All files are properly sized!")
        sys.exit(0)

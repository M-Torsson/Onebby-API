#!/usr/bin/env python3
"""
Security Check Script
Checks for potential hardcoded credentials in Python files
"""

import os
import re
from pathlib import Path

# Patterns to check for potential credentials
CREDENTIAL_PATTERNS = [
    (r'postgresql://[^:]+:[^@]+@', 'PostgreSQL connection string'),
    (r'mysql://[^:]+:[^@]+@', 'MySQL connection string'),
    (r'mongodb://[^:]+:[^@]+@', 'MongoDB connection string'),
    (r'password\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded password'),
    (r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', 'Hardcoded API key'),
    (r'secret[_-]?key\s*=\s*["\'][^"\']{20,}["\']', 'Hardcoded secret key'),
]

# Files/directories to skip
SKIP_PATTERNS = [
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.env',
    'node_modules',
    '.pytest_cache',
    'check_credentials.py',  # Skip this file itself
]

def should_skip(path):
    """Check if path should be skipped"""
    path_str = str(path)
    return any(skip in path_str for skip in SKIP_PATTERNS)

def check_file(file_path):
    """Check a single file for credentials"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for pattern, description in CREDENTIAL_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'file': file_path,
                    'line': line_num,
                    'description': description,
                    'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group()
                })
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
    
    return issues

def main():
    """Main function to check all Python files"""
    print("🔍 Checking for hardcoded credentials...\n")
    
    all_issues = []
    checked_files = 0
    
    # Get all Python files
    for py_file in Path('.').rglob('*.py'):
        if should_skip(py_file):
            continue
            
        checked_files += 1
        issues = check_file(py_file)
        all_issues.extend(issues)
    
    # Print results
    print(f"📊 Checked {checked_files} Python files\n")
    
    if all_issues:
        print("❌ FOUND POTENTIAL CREDENTIALS:\n")
        for issue in all_issues:
            print(f"  File: {issue['file']}")
            print(f"  Line: {issue['line']}")
            print(f"  Type: {issue['description']}")
            print(f"  Match: {issue['match']}")
            print()
        print(f"⚠️  Total issues found: {len(all_issues)}")
        print("\n⚠️  WARNING: Please review these files and use environment variables!")
        return 1
    else:
        print("✅ No hardcoded credentials found!")
        print("✅ All files appear to be using environment variables correctly.")
        return 0

if __name__ == '__main__':
    exit(main())

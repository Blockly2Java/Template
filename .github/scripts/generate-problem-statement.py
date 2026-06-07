#!/usr/bin/env python3
"""
Generate a Problem Statement Markdown file for Artemis exercise export.

This script reads the problem statement from the assignment's README.md and
produces a clean Markdown file suitable for Artemis import. It handles:
- Reading the source README
- Preserving task markers in the format: [task][description](testName1,testName2)
- Processing PlantUML URLs
- Cleaning up any formatting inconsistencies

Usage:
    python3 generate-problem-statement.py \
        --source parent/assignment/README.md \
        --output Problem-Statement.md
"""

import argparse
import re
import sys
from pathlib import Path


def process_problem_statement(source_content: str, shared_resources_url: str = None) -> str:
    """
    Process the problem statement content.
    
    Args:
        source_content: Raw markdown content from the source README
        shared_resources_url: Base URL for shared resources (e.g., PlantUML)
    
    Returns:
        Processed markdown string
    """
    result = source_content
    
    # If shared_resources_url is provided, update PlantUML URLs
    if shared_resources_url:
        # Pattern to match existing PlantUML proxy URLs
        # Matches: http://www.plantuml.com/plantuml/proxy?cache=no&fmt=svg&src=URL
        plantuml_pattern = r'http://www\.plantuml\.com/plantuml/proxy\?cache=no&fmt=svg&src=(.+?)(?=\s|$|")'
        
        def replace_plantuml_url(match):
            original_url = match.group(1).strip()
            # If it's a relative GitHub URL, convert to the shared resources URL
            if original_url.startswith('https://raw.githubusercontent.com/'):
                return shared_resources_url
            return match.group(0)  # Keep original if we can't process it
        
        result = re.sub(plantuml_pattern, replace_plantuml_url, result)
    
    # Clean up excessive whitespace (more than 3 consecutive newlines)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    
    # Ensure file ends with exactly two newlines
    result = result.rstrip() + '\n\n'
    
    return result


def extract_task_markers(content: str) -> list:
    """
    Extract all [task] markers from the content.
    
    Returns a list of dictionaries with marker information.
    """
    # Pattern: [task][description](testName1,testName2)
    pattern = r'\[task\]\[(.+?)\]\(([^)]+)\)'
    matches = re.finditer(pattern, content)
    
    tasks = []
    for match in matches:
        description = match.group(1)
        tests = [t.strip() for t in match.group(2).split(',')]
        tasks.append({
            'description': description,
            'tests': tests
        })
    
    return tasks


def validate_problem_statement(content: str) -> list:
    """
    Validate the problem statement and return any warnings.
    """
    warnings = []
    
    # Check for unescaped special characters in markdown
    # (This is a basic check - more comprehensive validation could be added)
    
    # Check for task markers without corresponding test names
    task_markers = extract_task_markers(content)
    if task_markers:
        for task in task_markers:
            if not task['tests']:
                warnings.append(f"Task marker without test names: {task['description']}")
    
    return warnings


def main():
    parser = argparse.ArgumentParser(
        description='Generate a Problem Statement Markdown file for Artemis'
    )
    parser.add_argument('--source', required=True, help='Source README.md path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--shared-resources-url', default=None,
                       help='Base URL for shared resources (PlantUML)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate the problem statement and print warnings')
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source file not found: {args.source}", file=sys.stderr)
        sys.exit(1)
    
    # Read source content
    with open(source_path, 'r', encoding='utf-8') as f:
        source_content = f.read()
        source_content = source_content.replace('[//]: #[task]','[task]').replace('[task][](','[task][ ](')
    
    # Ensure each test case name inside task markers is wrapped in parentheses.
    # Fixes cases where the source has "testName" but expects "testName()".
    # Handles both broken source (no parens) and correct source (already has parens).
    # Also skips test group markers like structStructural[all] — these are left unchanged.
    # Uses line-by-line processing with a 4-group pattern:
    #   Group 1: "[task][ ]"  Group 2: "("  Group 3: test list  Group 4: ")"
    def fix_test_case_parens(match):
        marker = match.group(1)   # e.g., "[task][ ]"
        open_paren = match.group(2)  # e.g., "("
        test_list = match.group(3)   # e.g., "testMenschGetX,testMenschGetY" or "structStructural[all]"
        close_paren = match.group(4)  # e.g., ")"
        tests = [t.strip() for t in test_list.split(',')]
        fixed_tests = []
        for t in tests:
            # Skip group markers like structStructural[all], testPartial[partial] etc.
            if '[' in t:
                fixed_tests.append(t)
            elif t.endswith('()'):
                # Already has parentheses, leave as-is
                fixed_tests.append(t)
            else:
                # Add parentheses to test case names that are missing them
                fixed_tests.append(f'{t}()')
        return marker + open_paren + ','.join(fixed_tests) + close_paren
    
    source_content = re.sub(
        r'^(\[task\]\[ \])(\()([^)]+)(\))\s*$',
        fix_test_case_parens,
        source_content,
        flags=re.MULTILINE
    )
    
    # Process the content
    result = process_problem_statement(source_content, args.shared_resources_url)
    
    # Validate if requested
    if args.validate:
        warnings = validate_problem_statement(result)
        for warning in warnings:
            print(f"Warning: {warning}", file=sys.stderr)
    
    # Write output
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"Problem statement written to: {output_path}")


if __name__ == '__main__':
    main()
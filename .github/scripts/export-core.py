#!/usr/bin/env python3
"""
Shared core logic for Artemis exercise export.

This module provides functions for creating ZIP files from repository directories
and packaging them into the final Artemis export ZIP. Both the GitHub Actions
workflow and the local test script use this module to ensure consistency.

Usage:
    python3 export-core.py create-zips \
        --short-name "template" \
        --template-dir template \
        --solution-dir solution \
        --tests-dir tests

    python3 export-core.py package-export \
        --short-name "template" \
        --id "20534" \
        --course-prefix "testmtgherrmann" \
        --output-dir .
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def create_repo_zip(repo_dir: str, output_zip: str, exclude_git_objects: bool = True) -> str:
    """
    Create a ZIP file from a repository directory.
    
    Args:
        repo_dir: Path to the repository directory
        output_zip: Output ZIP file path
        exclude_git_objects: If True, exclude large git object files
    
    Returns:
        Path to the created ZIP file
    """
    repo_path = Path(repo_dir)
    if not repo_path.exists():
        print(f"Error: Repository directory not found: {repo_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Build zip command arguments
    cmd = ["zip", "-r", output_zip, "."]
    
    if exclude_git_objects:
        cmd.extend([
            "-x", ".git/objects/*",
            "-x", ".git/refs/*",
            "-x", ".git/FETCH_HEAD",
            "-x", ".git/ORIG_HEAD",
            "-x", ".git/logs/*",
        ])
    
    result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error creating ZIP for {repo_dir}:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    
    print(f"Created ZIP: {output_zip} ({repo_dir})")
    return output_zip


def create_all_zips(
    short_name: str,
    template_dir: str,
    solution_dir: str,
    tests_dir: str,
    output_dir: str = "."
) -> list:
    """
    Create ZIP files for template (exercise), solution, and tests repositories.
    
    Args:
        short_name: Exercise short name used in ZIP filenames
        template_dir: Path to template repository directory
        solution_dir: Path to solution repository directory
        tests_dir: Path to tests repository directory
        output_dir: Directory to write ZIP files
    
    Returns:
        List of created ZIP file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    
    exercise_zip = os.path.join(output_dir, f"{short_name}-exercise.zip")
    solution_zip = os.path.join(output_dir, f"{short_name}-solution.zip")
    tests_zip = os.path.join(output_dir, f"{short_name}-tests.zip")
    
    create_repo_zip(template_dir, exercise_zip)
    create_repo_zip(solution_dir, solution_zip)
    create_repo_zip(tests_dir, tests_zip)
    
    return [exercise_zip, solution_zip, tests_zip]


def package_export(
    short_name: str,
    exercise_id: str,
    course_prefix: str,
    output_dir: str = ".",
    json_file: str = None,
    md_file: str = None
) -> str:
    """
    Package all components into the final Artemis export ZIP.
    
    Args:
        short_name: Exercise short name
        exercise_id: Artemis exercise ID
        course_prefix: Course/username prefix
        output_dir: Directory containing the component files
        json_file: Path to exercise details JSON (auto-generated if not provided)
        md_file: Path to problem statement MD (auto-generated if not provided)
    
    Returns:
        Path to the created export ZIP
    """
    if json_file is None:
        json_file = os.path.join(output_dir, f"Exercise-Details-{short_name}.json")
    if md_file is None:
        md_file = os.path.join(output_dir, f"Problem-Statement-{short_name}.md")
    
    # Check that component files exist
    for filepath in [json_file, md_file]:
        if not os.path.exists(filepath):
            print(f"Error: Required file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
    
    exercise_zip = os.path.join(output_dir, f"{short_name}-exercise.zip")
    solution_zip = os.path.join(output_dir, f"{short_name}-solution.zip")
    tests_zip = os.path.join(output_dir, f"{short_name}-tests.zip")
    
    for filepath in [exercise_zip, solution_zip, tests_zip]:
        if not os.path.exists(filepath):
            print(f"Error: Required ZIP file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
    
    # Generate timestamp and output filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    #output_filename = f"{course_prefix}-{short_name}-{exercise_id}-{timestamp}.zip"
    output_filename = f"{short_name}-{timestamp}.zip"
    output_path = os.path.join(output_dir, output_filename)
    
    import shutil
    json_name = os.path.basename(json_file)
    md_name = os.path.basename(md_file)
    
    dest_json = os.path.join(output_dir, json_name)
    dest_md = os.path.join(output_dir, md_name)
    
    if os.path.abspath(json_file) != os.path.abspath(dest_json):
        shutil.copy2(json_file, dest_json)
    if os.path.abspath(md_file) != os.path.abspath(dest_md):
        shutil.copy2(md_file, dest_md)

    # Create the final export ZIP using basenames relative to output_dir
    cmd = [
        "zip", output_path,
        json_name,
        md_name,
        f"{short_name}-exercise.zip",
        f"{short_name}-solution.zip",
        f"{short_name}-tests.zip"
    ]
    
    result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error creating export ZIP:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    
    print(f"Created export ZIP: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Shared core logic for Artemis exercise export'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # create-zips command
    create_zips_parser = subparsers.add_parser('create-zips', help='Create ZIP files for all repos')
    create_zips_parser.add_argument('--short-name', required=True, help='Exercise short name')
    create_zips_parser.add_argument('--template-dir', required=True, help='Template repo directory')
    create_zips_parser.add_argument('--solution-dir', required=True, help='Solution repo directory')
    create_zips_parser.add_argument('--tests-dir', required=True, help='Tests repo directory')
    create_zips_parser.add_argument('--output-dir', default='.', help='Output directory for ZIPs')
    
    # package-export command
    package_export_parser = subparsers.add_parser('package-export', help='Package final export ZIP')
    package_export_parser.add_argument('--short-name', required=True, help='Exercise short name')
    package_export_parser.add_argument('--id', '--exercise-id', required=True, help='Exercise ID')
    package_export_parser.add_argument('--course-prefix', required=True, help='Course prefix')
    package_export_parser.add_argument('--output-dir', default='.', help='Output directory')
    package_export_parser.add_argument('--json-file', default=None, help='Exercise details JSON path')
    package_export_parser.add_argument('--md-file', default=None, help='Problem statement MD path')
    
    args = parser.parse_args()
    
    if args.command == 'create-zips':
        zips = create_all_zips(
            short_name=args.short_name,
            template_dir=args.template_dir,
            solution_dir=args.solution_dir,
            tests_dir=args.tests_dir,
            output_dir=args.output_dir
        )
        print(f"Created {len(zips)} ZIP files: {', '.join(zips)}")
    
    elif args.command == 'package-export':
        output = package_export(
            short_name=args.short_name,
            exercise_id=args.id,
            course_prefix=args.course_prefix,
            output_dir=args.output_dir,
            json_file=args.json_file,
            md_file=args.md_file
        )
        print(f"Export ZIP created: {output}")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
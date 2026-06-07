#!/usr/bin/env python3
"""
Generate an Artemis Exercise-Details JSON file from command-line arguments.

This script creates a JSON configuration file that can be imported into Artemis
for programming exercises. It uses a template file with placeholders and
substitutes values from command-line arguments.

Template Placeholders:
    {{ID}} - Exercise ID
    {{TITLE}} - Exercise title
    {{SHORT_NAME}} - Exercise short name (lowercase, no spaces)
    {{MAX_POINTS}} - Maximum points
    {{COURSE_PREFIX}} - Course/username prefix
    {{PACKAGE_NAME}} - Java package name
    {{BUILD_PLAN_CONFIG}} - JSON string of build configuration
Usage:
    python3 generate-exercise-details.py \
        --title "My Exercise" \
        --short-name "myexercise" \
        --id "12345" \
        --course-prefix "testmtgherrmann" \
        --max-points "10.0" \
        --package-name "b2j.test" \
        --output Exercise-Details.json \
        --template-file exercise-details-template.json
"""

import argparse
import json
import sys
from pathlib import Path


def load_template(template_file: str) -> dict:
    """Load the exercise details template JSON file."""
    template_path = Path(template_file)
    if not template_path.exists():
        print(f"Error: Template file not found: {template_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_build_plan_config(docker_image: str, build_script: str) -> str:
    """Generate the buildPlanConfiguration JSON string."""
    config = {
        "phases": [{
            "name": "gradle",
            "script": build_script,
            "condition": "ALWAYS",
            "forceRun": False,
            "resultPaths": ["**/test-results/test/*.xml"]
        }],
        "dockerImage": docker_image
    }
    return json.dumps(config)


def substitute_template(template: dict, replacements: dict) -> dict:
    """
    Recursively substitute placeholders in a dictionary.
    
    Handles nested dictionaries and lists by traversing the structure
    and replacing string values that contain placeholders.
    """
    if isinstance(template, dict):
        return {key: substitute_template(value, replacements) for key, value in template.items()}
    elif isinstance(template, list):
        return [substitute_template(item, replacements) for item in template]
    elif isinstance(template, str):
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        # Try to convert numeric strings back to numbers where appropriate
        return template
    else:
        return template


def generate_exercise_details(
    title: str,
    short_name: str,
    exercise_id: str,
    course_prefix: str,
    max_points: str = "10.0",
    package_name: str = "b2j.test",
    docker_image: str = "ghcr.io/valentinherrmann/artemis-maven-docker:latest",
    build_script: str = "chmod +x gradlew\n./gradlew clean test",
    template_file: str = None
) -> dict:
    """Generate the exercise details dictionary from template or defaults."""
    
    short_name_clean = short_name.lower().replace(' ', '')
    project_key = course_prefix.upper() + short_name_clean.upper()
    build_plan_config = generate_build_plan_config(docker_image, build_script)
    
    replacements = {
        '{{ID}}': exercise_id,
        '{{TITLE}}': title,
        '{{SHORT_NAME}}': short_name_clean,
        '{{MAX_POINTS}}': max_points,
        '{{COURSE_PREFIX}}': course_prefix,
        '{{PACKAGE_NAME}}': package_name,
        '{{BUILD_PLAN_CONFIG}}': build_plan_config
    }
    
    if template_file:
        template = load_template(template_file)
        return substitute_template(template, replacements)
    else:
        # Generate from scratch with sensible defaults
        return {
            "type": "programming",
            "id": int(exercise_id),
            "title": title,
            "shortName": short_name_clean,
            "maxPoints": float(max_points),
            "bonusPoints": 0.0,
            "assessmentType": "AUTOMATIC",
            "dueDate": None,
            "mode": "INDIVIDUAL",
            "allowComplaintsForAutomaticAssessments": False,
            "allowFeedbackRequests": False,
            "includedInOverallScore": "NOT_INCLUDED",
            "problemStatement": "",
            "presentationScoreEnabled": False,
            "secondCorrectionEnabled": False,
            "course": {
                "id": None,
                "title": f"Exercise: {title}",
                "shortName": course_prefix,
                "studentGroupName": f"artemis-{course_prefix}-students",
                "teachingAssistantGroupName": f"artemis-{course_prefix}-tutors",
                "editorGroupName": f"artemis-{course_prefix}-editors",
                "instructorGroupName": f"artemis-{course_prefix}-instructors",
                "startDate": None,
                "endDate": None,
                "semester": None,
                "testCourse": True,
                "courseInformationSharingConfiguration": "COMMUNICATION_AND_MESSAGING",
                "maxComplaints": 3,
                "maxTeamComplaints": 3,
                "maxComplaintTimeDays": 7,
                "maxRequestMoreFeedbackTimeDays": 7,
                "maxComplaintTextLimit": 2000,
                "maxComplaintResponseTextLimit": 2000,
                "color": "#ffb2b2",
                "timeZone": "Europe/Berlin",
                "learningPathsEnabled": False,
                "studentCourseAnalyticsDashboardEnabled": False,
                "requestMoreFeedbackEnabled": True,
                "trainingEnabled": False,
                "complaintsEnabled": True,
                "faqEnabled": True
            },
            "plagiarismDetectionConfig": {
                "continuousPlagiarismControlEnabled": False,
                "continuousPlagiarismControlPostDueDateChecksEnabled": False,
                "continuousPlagiarismControlPlagiarismCaseStudentResponsePeriod": 7,
                "similarityThreshold": 90,
                "minimumScore": 0,
                "minimumSize": 50
            },
            "testRepositoryUri": None,
            "allowOnlineEditor": False,
            "allowOfflineIde": True,
            "allowOnlineIde": False,
            "staticCodeAnalysisEnabled": False,
            "programmingLanguage": "JAVA",
            "packageName": package_name,
            "showTestNamesToStudents": True,
            "testCasesChanged": True,
            "projectKey": project_key,
            "projectType": "PLAIN_GRADLE",
            "releaseTestsWithExampleSolution": False,
            "buildConfig": {
                "id": None,
                "sequentialTestRuns": False,
                "branch": "main",
                "buildPlanConfiguration": build_plan_config,
                "checkoutSolutionRepository": False,
                "timeoutSeconds": 0,
                "allowBranching": False,
                "branchRegex": ".*"
            },
            "exerciseType": "programming",
            "defaultTestCaseVisibility": "ALWAYS",
            "studentAssignedTeamIdComputed": False,
            "gradingInstructionFeedbackUsed": False,
            "visibleToStudents": True,
            "teamMode": False
        }


def main():
    parser = argparse.ArgumentParser(
        description='Generate an Artemis Exercise-Details JSON file'
    )
    parser.add_argument('--title', required=True, help='Exercise title')
    parser.add_argument('--short-name', required=True, help='Exercise short name (lowercase, no spaces)')
    parser.add_argument('--id', required=True, help='Artemis Exercise ID')
    parser.add_argument('--course-prefix', required=True, help='Course/username prefix')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--max-points', default='10.0', help='Maximum points')
    parser.add_argument('--package-name', default='b2j.test', help='Java package name')
    parser.add_argument('--docker-image', default='ghcr.io/valentinherrmann/artemis-maven-docker:latest',
                       help='Docker image for building')
    parser.add_argument('--build-script', default='chmod +x gradlew\n./gradlew clean test',
                       help='Build script commands')
    parser.add_argument('--template-file', default=None, help='Path to template JSON file')
    
    args = parser.parse_args()
    
    exercise_details = generate_exercise_details(
        title=args.title,
        short_name=args.short_name,
        exercise_id=args.id,
        course_prefix=args.course_prefix,
        max_points=args.max_points,
        package_name=args.package_name,
        docker_image=args.docker_image,
        build_script=args.build_script,
        template_file=args.template_file
    )
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(exercise_details, f, indent=4, ensure_ascii=False)
    
    print(f"Exercise details written to: {output_path}")


if __name__ == '__main__':
    main()
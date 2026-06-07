#!/usr/bin/env bash
set -euo pipefail

GITHUB_ORG="Blockly2Java"
NAME=""
PARENT_BRANCH="main"
TEMPLATE_BRANCH="main"
SOLUTION_BRANCH="main"
KEEP_TEMP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --name) NAME="$2"; shift 2 ;;
        --github-org) GITHUB_ORG="$2"; shift 2 ;;
        --parent-branch) PARENT_BRANCH="$2"; shift 2 ;;
        --template-branch) TEMPLATE_BRANCH="$2"; shift 2 ;;
        --solution-branch) SOLUTION_BRANCH="$2"; shift 2 ;;
        --keep-temp) KEEP_TEMP=true; shift ;;
        --help)
            echo "Usage: $0 --name NAME [--github-org ORG] [--parent-branch BRANCH] [--template-branch BRANCH] [--solution-branch BRANCH] [--keep-temp] [--help]"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "$NAME" ]]; then
    echo "Error: --name is required."
    exit 1
fi

# Title, short-name, and repo-base are always identical
TITLE="$NAME"
SHORT_NAME="$NAME"
REPO_BASE="$NAME"

# Always use default values for course-prefix and id
ID="1"
COURSE_PREFIX="testmtgherrmann"

# Derive repo names from name/org
PARENT_REPO="${GITHUB_ORG}/${REPO_BASE}"
TEMPLATE_REPO="${GITHUB_ORG}/${REPO_BASE}_template"
SOLUTION_REPO="${GITHUB_ORG}/${REPO_BASE}_solution"

echo "Using github-org: $GITHUB_ORG"
echo "Using name:       $NAME"
echo "Parent repo:      $PARENT_REPO (branch: $PARENT_BRANCH)"
echo "Template repo:    $TEMPLATE_REPO (branch: $TEMPLATE_BRANCH)"
echo "Solution repo:    $SOLUTION_REPO (branch: $SOLUTION_BRANCH)"

STAGING_DIR=$(mktemp -d)
echo "Created staging directory: $STAGING_DIR"

cleanup() {
    if [[ "$KEEP_TEMP" == "false" ]]; then
        if ls "$STAGING_DIR"/*.zip 1>/dev/null 2>&1; then
            mkdir -p "$WORKSPACE_DIR/Artemis_Export"
            cp "$STAGING_DIR"/*.zip "$WORKSPACE_DIR/Artemis_Export/"
            echo "Copied export ZIP to Artemis_Export directory: $WORKSPACE_DIR/Artemis_Export"
        fi
        echo "Cleaning up temporary directory: $STAGING_DIR"
        rm -rf "$STAGING_DIR"
    else
        echo "Keeping temporary directory for debugging: $STAGING_DIR"
    fi
}
trap cleanup EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "SCRIPT_DIR: $SCRIPT_DIR"
echo "PARENT_DIR: $PARENT_DIR"
echo "WORKSPACE_DIR: $WORKSPACE_DIR"

clone_repos() {
    echo "Cloning GitHub repos into staging directory..."
    local repos=(
        "${PARENT_REPO}:${STAGING_DIR}/parent:${PARENT_BRANCH}"
        "${TEMPLATE_REPO}:${STAGING_DIR}/template:${TEMPLATE_BRANCH}"
        "${SOLUTION_REPO}:${STAGING_DIR}/solution:${SOLUTION_BRANCH}"
    )
    for entry in "${repos[@]}"; do
        IFS=':' read -r repo staging_dir branch <<< "$entry"
        echo "  Cloning ${repo} (branch: ${branch}) -> ${staging_dir} ..."
        git clone --depth 1 --branch "${branch}" "https://github.com/${repo}.git" "${staging_dir}"
    done
    echo "All repos cloned successfully."
}

echo "Copying local scripts to staging directory..."
cp "$SCRIPT_DIR/generate-exercise-details.py" "$STAGING_DIR/"
cp "$SCRIPT_DIR/generate-problem-statement.py" "$STAGING_DIR/"
cp "$SCRIPT_DIR/export-core.py" "$STAGING_DIR/"
cp "$SCRIPT_DIR/exercise-details-template.json" "$STAGING_DIR/"

echo "Cloning repos from GitHub..."
clone_repos

echo "Generating exercise details JSON..."
python3 "$STAGING_DIR/generate-exercise-details.py" \
    --template-file "$STAGING_DIR/exercise-details-template.json" \
    --title "$TITLE" \
    --short-name "$SHORT_NAME" \
    --id "$ID" \
    --course-prefix "$COURSE_PREFIX" \
    --output "$STAGING_DIR/Exercise-Details-${SHORT_NAME}.json"

echo "Generating problem statement Markdown..."
python3 "$STAGING_DIR/generate-problem-statement.py" \
    --source "$STAGING_DIR/template/README.md" \
    --output "$STAGING_DIR/Problem-Statement-${SHORT_NAME}.md"

echo "Merging problem statement into exercise details JSON..."
python3 -c "
import json, sys
md_path, json_path = sys.argv[1], sys.argv[2]
with open(md_path) as f:
    md_content = f.read()
with open(json_path) as f:
    json_data = json.load(f)
json_data['problemStatement'] = md_content
with open(json_path, 'w') as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)
print(f'Problem statement merged ({len(md_content)} chars) into {json_path}')
" "$STAGING_DIR/Problem-Statement-${SHORT_NAME}.md" "$STAGING_DIR/Exercise-Details-${SHORT_NAME}.json"

echo "Creating exercise, solution, and tests ZIPs..."
python3 "$STAGING_DIR/export-core.py" create-zips \
    --short-name "$SHORT_NAME" \
    --template-dir "$STAGING_DIR/template" \
    --solution-dir "$STAGING_DIR/solution" \
    --tests-dir "$STAGING_DIR/parent" \
    --output-dir "$STAGING_DIR"

echo "Packaging final export ZIP..."
python3 "$STAGING_DIR/export-core.py" package-export \
    --short-name "$SHORT_NAME" \
    --id "$ID" \
    --course-prefix "$COURSE_PREFIX" \
    --json-file "$STAGING_DIR/Exercise-Details-${SHORT_NAME}.json" \
    --md-file "$STAGING_DIR/Problem-Statement-${SHORT_NAME}.md" \
    --output-dir "$STAGING_DIR"

echo "Export ZIP created in staging directory."
ls -la "$STAGING_DIR"/*.zip

echo "Done!"
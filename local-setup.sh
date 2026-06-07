#!/usr/bin/env bash
# Clones sibling repos (template, solution, tests) alongside parent/ for local development.
# Run once after cloning the parent repo into a new folder.
# Self-discovering: derives org and exercise name from git remote — no editing needed.
#
# Usage:
#   git clone git@github.com:Org/MyExercise_parent.git MyExercise
#   cd MyExercise && ./local-setup.sh
#
# Result:
#   MyExercise/
#   ├── VS-Code.code-workspace (copied from root-template)
#   ├── parent/       ← Git repo (MyExercise_parent)
#   ├── template/     ← Git repo (MyExercise_template)
#   ├── solution/     ← Git repo (MyExercise_solution)
#   └── tests/        ← Git repo (MyExercise_tests)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$(basename "$SCRIPT_DIR")" != "parent" ]; then
  echo "Restructuring repository layout..."
  WORKSPACE_ROOT="$SCRIPT_DIR"
  cd "$WORKSPACE_ROOT"

  # Derive org and exercise name from the git remote of THIS repo (parent)
  REMOTE_URL=$(git remote get-url origin)
  ORG=$(echo "$REMOTE_URL" | sed -E 's|.*[:/]([^/]+)/[^/]+\.git.*|\1|')
  EXERCISE=$(echo "$REMOTE_URL" | sed -E 's|.*[:/][^/]+/([^/]+)\.git.*|\1|')

  # Create parent directory
  mkdir -p parent

  # Move all files and directories into parent/, excluding parent/ itself
  for file in .* *; do
    if [ "$file" != "." ] && [ "$file" != ".." ] && [ "$file" != "parent" ]; then
      mv "$file" parent/
    fi
  done

  # Copy root-template files to the workspace root
  if [ -d "parent/root-template" ]; then
    cp -a parent/root-template/. ./
  fi
else
  WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure ORG and EXERCISE are retrieved if they were not set during restructuring
if [ -z "$ORG" ] || [ -z "$EXERCISE" ]; then
  REMOTE_URL=$(git -C "$WORKSPACE_ROOT/parent" remote get-url origin)
  ORG=$(echo "$REMOTE_URL" | sed -E 's|.*[:/]([^/]+)/[^/]+\.git.*|\1|')
  EXERCISE=$(echo "$REMOTE_URL" | sed -E 's|.*[:/][^/]+/([^/]+)\.git.*|\1|')
fi

echo "Organisation : $ORG"
echo "Exercise     : $EXERCISE"
echo ""

BASE="git@github.com:${ORG}"

# Clone sibling repos into WORKSPACE_ROOT
for sub in template solution tests; do
  SUB_DIR="$WORKSPACE_ROOT/$sub"
  if [ ! -d "$SUB_DIR/.git" ]; then
    echo "Cloning ${EXERCISE}_${sub}..."
    git clone "${BASE}/${EXERCISE}_${sub}.git" "$SUB_DIR"
  else
    echo "$sub already present, pulling latest..."
    git -C "$SUB_DIR" pull --ff-only
  fi
done

echo ""
echo "Done! Structure:"
echo "  $WORKSPACE_ROOT/"
echo "  ├── VS-Code.code-workspace"
echo "  ├── parent/       (this repo)"
echo "  ├── template/     (student code)"
echo "  ├── solution/     (reference solution)"
echo "  └── tests/        (test harness)"
echo ""
echo "Run 'cd $WORKSPACE_ROOT && gradle testSolution' to verify."
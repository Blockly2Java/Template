#!/bin/bash

REPOS=("parent" "solution" "template" "tests")

echo "=== Pulling changes from all repos ==="
echo ""

for repo in "${REPOS[@]}"; do
  echo "Pulling changes in $repo..."
  (cd "$repo" && git pull)
  if [ $? -eq 0 ]; then
    echo "✓ $repo updated successfully"
  else
    echo "✗ Failed to update $repo"
  fi
  echo ""
done

echo "=== Done ==="
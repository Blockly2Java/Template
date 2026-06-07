#!/bin/bash

REPOS=("parent" "solution" "template" "tests")

echo "=== Pushing changes to all repos ==="
echo ""

for repo in "${REPOS[@]}"; do
  echo "Pushing changes to $repo..."
  (cd "$repo" && git push)
  if [ $? -eq 0 ]; then
    echo "✓ $repo pushed successfully"
  else
    echo "✗ Failed to push $repo"
  fi
  echo ""
done

echo "=== Done ==="
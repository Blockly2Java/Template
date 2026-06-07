#!/bin/bash

REPOS=("parent" "solution" "template" "tests")

echo "=== Committing changes in all repos ==="
echo ""
read -p "Enter commit message: " commit_message

for repo in "${REPOS[@]}"; do
  echo "Committing changes in $repo..."
  (cd "$repo" && git commit -a -m "$commit_message" ) 
  if [ $? -eq 0 ]; then
    echo "✓ $repo committed successfully"
  else
    echo "✗ Failed to commit $repo"
  fi
  echo ""
done

echo "=== Done ==="
#!/bin/bash

# --- CONFIGURATION ---
GALAXY_FILE="galaxy.yml"
GALAXY_API_KEY="d7a8c0f3227893e2abb40cf9567a782ee683fdc6"
GH_TOKEN="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"
USERNAME="polaamgad88"
REPO_NAME="openshift-collection"

# 1. Detect and Bump Version
echo "🔍 Detecting current version..."
CURRENT_VERSION=$(grep '^version:' $GALAXY_FILE | awk '{print $2}')
BASE_VERSION=$(echo $CURRENT_VERSION | cut -d. -f1-2)
PATCH_VERSION=$(echo $CURRENT_VERSION | cut -d. -f3)
NEW_VERSION="${BASE_VERSION}.$((PATCH_VERSION + 1))"

echo "📈 Bumping version: $CURRENT_VERSION -> $NEW_VERSION"
sed -i "s/^version: .*/version: $NEW_VERSION/" $GALAXY_FILE

# 2. Build the Collection
echo "📦 Building collection v$NEW_VERSION..."
ansible-galaxy collection build --force

# 3. Publish to Ansible Galaxy
TARBALL="polaamgad88-openshift_day2-${NEW_VERSION}.tar.gz"
echo "📤 Publishing to Galaxy..."
ansible-galaxy collection publish "$TARBALL" --api-key "$GALAXY_API_KEY"

# 4. Push to GitHub using Token
echo "🖥️ Syncing with GitHub..."
git add .
git commit -m "Release v$NEW_VERSION: Automated Deployment"

# Set the remote URL with the token for silent authentication
git remote set-url origin "https://${USERNAME}:${GH_TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git"
git push origin main

echo "✅ DONE! v$NEW_VERSION is live on Galaxy and GitHub."
rm "$TARBALL"

#!/bin/bash

# Please make sure the remote has already been added before running the script
TEMPLATE_URL="https://github.com/IQAndreas/gh-pages-template.git"
TEMPLATE_NAME="gh-pages-template"
TEMPLATE_BRANCH="gh-pages-minimal"

git fetch $TEMPLATE_NAME || exit 1;
git merge $TEMPLATE_NAME/$TEMPLATE_BRANCH --no-ff --no-commit

echo "Changes applied. Please double check the merged file (manually correcting any conflicts if necessary) and then merge the changes." && exit 0;

#!/bin/bash

ORIGIN_URL=`git config --get remote.origin.url`
TEMPLATE_URL="https://github.com/IQAndreas/gh-pages-template.git"
TEMPLATE_NAME="gh-pages-template"
TEMPLATE_BRANCH="gh-pages-minimal" #Can also be set to 'gh-pages'
TARGET_DIRECTORY="gh-pages"

git clone "$TEMPLATE_URL" --origin "$TEMPLATE_NAME" --branch "$TEMPLATE_BRANCH" "$TARGET_DIRECTORY"
cd "$TARGET_DIRECTORY"
if [ "$TEMPLATE_BRANCH" != "gh-pages" ]; then
	git checkout -b gh-pages
	git branch -d "$TEMPLATE_BRANCH"
fi
git remote add origin "$ORIGIN_URL"
git push origin -u gh-pages


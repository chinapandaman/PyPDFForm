if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

python ./scripts/bump_version.py

git add ./PyPDFForm/__init__.py mkdocs.yml
BRANCH=$(git symbolic-ref HEAD 2>/dev/null)
BRANCH=${BRANCH##refs/heads/}
git commit -m "${BRANCH}: bump version"
git push --set-upstream origin ${BRANCH}

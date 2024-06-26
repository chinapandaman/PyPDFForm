if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

BRANCH=$(git symbolic-ref HEAD 2>/dev/null)
BRANCH=${BRANCH##refs/heads/}

if python ./scripts/bump_version.py ${BRANCH} ; then
  git add ./PyPDFForm/__init__.py mkdocs.yml SECURITY.md
  git commit -m "${BRANCH}: bump version"
  git push --set-upstream origin ${BRANCH}
fi

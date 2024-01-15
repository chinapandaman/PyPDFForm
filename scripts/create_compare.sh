if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

pytest -v -s --regenerate=1

for f in $(git diff --name-only ./pdf_samples); do
  python ./scripts/create_compare.py "$PWD/${f}"
done

git restore --source=HEAD --staged --worktree -- ./pdf_samples

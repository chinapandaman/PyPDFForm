if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

pytest --regenerate=1

BEFORE=()

for f in $(git diff --name-only ./pdf_samples); do
  BEFORE+=("$PWD/${f}")
  python ./scripts/create_pdf_diff.py "$PWD/${f}"
done

git restore --source=HEAD --staged --worktree -- ./pdf_samples

for i in "${BEFORE[@]}"; do
  python ./scripts/open_pdf_diff.py "$i"
  read -p "Press any key to continue..."$'\n' -n1 -s -r
done

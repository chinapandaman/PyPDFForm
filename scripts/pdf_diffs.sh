if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

rm -f ./temp/*.png

PYTHONPATH=. pytest -m 'not cli_test' --regenerate=1

BEFORE=()

for f in $(git diff --name-only ./pdf_samples ./docs/pdfs); do
  BEFORE+=("$PWD/${f}")
  python ./scripts/create_pdf_diff.py "$PWD/${f}"
done

git restore --source=HEAD --staged --worktree -- ./pdf_samples ./docs/pdfs

TOTAL=${#BEFORE[@]}
COUNT=1
SEPARATOR="==============="

for i in "${BEFORE[@]}"; do
  printf '%s\n%s/%s\n%s\n' "$SEPARATOR" "$COUNT" "$TOTAL" "$SEPARATOR"
  python ./scripts/open_pdf_diff.py "$i"
  read -p "Press any key to continue..."$'\n' -n1 -s -r
  rm -f ./temp/*.png
  COUNT=$((COUNT + 1))
done

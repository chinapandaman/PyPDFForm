if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

# Regenerated PDFs are written here instead of over the expected PDFs, so the
# working tree and the index are never modified.
ARTIFACTS="./temp/pdf_diffs"
AFTER="$ARTIFACTS/after"

rm -rf "$ARTIFACTS"
mkdir -p "$AFTER"
echo "Comparison artifacts: $ARTIFACTS"

PYTHONPATH=. pytest -m 'not cli_test' --regenerate=1 --regenerate-dir="$AFTER"
STATUS=$?

# pytest exits with 1 when tests fail, which is expected for changed PDFs.
if [ "$STATUS" -gt 1 ]; then
  echo "PDF generation failed with exit status $STATUS. Comparison artifacts: $ARTIFACTS" >&2
  exit "$STATUS"
fi

CHANGED=()

for f in $(cd "$AFTER" && find . -type f | sort); do
  f="${f#./}"
  if cmp -s "$AFTER/$f" "./$f"; then
    rm -f "$AFTER/$f"
  else
    CHANGED+=("$f")
  fi
done

find "$AFTER" -mindepth 1 -type d -empty -delete

TOTAL=${#CHANGED[@]}
COUNT=1
SEPARATOR="==============="

for i in "${CHANGED[@]}"; do
  printf '%s\n%s/%s\n%s\n' "$SEPARATOR" "$COUNT" "$TOTAL" "$SEPARATOR"
  python ./scripts/open_pdf_diff.py "$i" "$AFTER/$i" "$ARTIFACTS"
  read -p "Press any key to continue..."$'\n' -n1 -s -r
  rm -f "$ARTIFACTS"/*.png
  COUNT=$((COUNT + 1))
done

echo "Changed PDFs: $TOTAL. Regenerated versions: $AFTER"

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

PYTHONPATH=. pytest -n auto -m 'snapshot and not cli_test' --regenerate=1 --regenerate-dir="$AFTER"
STATUS=$?

# pytest exits with 1 when tests fail, which is expected for changed PDFs. It
# exits with 4 when two tests own the same expected PDF, since the one written
# last would hide the other.
if [ "$STATUS" -gt 1 ]; then
  echo "PDF generation failed with exit status $STATUS. Comparison artifacts: $ARTIFACTS" >&2
  exit "$STATUS"
fi

# A test that compares with another test's expected PDF writes its differing
# version as same_as/<test>/<expected PDF>, so it doesn't replace the owner's.
# <test> has no slash, and the owners' versions are under pdf_samples/ or docs/.
expected_pdf() {
  case "$1" in
    same_as/*)
      local rest="${1#same_as/}"
      echo "${rest#*/}"
      ;;
    *) echo "$1" ;;
  esac
}

CHANGED=()

for f in $(cd "$AFTER" && find . -type f | sort); do
  f="${f#./}"
  if cmp -s "$AFTER/$f" "./$(expected_pdf "$f")"; then
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
  python ./scripts/open_pdf_diff.py "$(expected_pdf "$i")" "$AFTER/$i" "$ARTIFACTS"
  read -p "Press any key to continue..."$'\n' -n1 -s -r
  rm -f "$ARTIFACTS"/*.png
  COUNT=$((COUNT + 1))
done

echo "Changed PDFs: $TOTAL. Regenerated versions: $AFTER"

if [ "$STATUS" -eq 1 ] && [ "$TOTAL" -eq 0 ]; then
  echo "Tests failed, but no regenerated PDF differs from its expected PDF. See the failures above." >&2
  exit 1
fi

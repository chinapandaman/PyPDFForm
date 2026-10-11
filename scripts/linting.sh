set -e

if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

status=0

run_check() {
  printf '\nRunning: %s\n' "$*"
  local check_status=0
  "$@" || check_status=$?
  if [ "$check_status" -ne 0 ]; then
    printf 'Failed: %s (exit status %s)\n' "$*" "$check_status" >&2
    status=1
  fi
}

run_check pylint PyPDFForm/
run_check pyright .
run_check ruff check .
run_check python ./scripts/doc_examples_type_check.py

exit "$status"

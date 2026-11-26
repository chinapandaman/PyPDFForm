if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

PYTHONPATH=. pytest -n auto -m 'not cli_test' --regenerate=1

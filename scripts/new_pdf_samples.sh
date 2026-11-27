if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

PYTHONPATH=. pytest -m 'snapshot and not cli_test' --regenerate=1

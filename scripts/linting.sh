if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

pylint PyPDFForm/
pyright .
ruff check --ignore I .
python ./scripts/doc_examples_type_check.py

if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

PYTHONPATH=$PYTHONPATH:$(pwd)/PyPDFForm
export PYTHONPATH
pytest -v

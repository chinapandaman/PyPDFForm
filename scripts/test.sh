if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv-linux/bin/activate"
fi

PYTHONPATH=$PYTHONPATH:$(pwd)/PyPDFForm
export PYTHONPATH
pytest -v

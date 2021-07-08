if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv-linux/bin/activate"
fi

coverage run -m pytest -v -s

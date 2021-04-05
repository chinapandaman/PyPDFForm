if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv-linux/bin/activate"
fi

pytest -v

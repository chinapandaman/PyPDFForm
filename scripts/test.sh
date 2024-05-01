if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

coverage run -m pytest -s && coverage report --fail-under=100

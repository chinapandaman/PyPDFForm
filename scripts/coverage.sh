if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv-linux/bin/activate"
fi

rm -rf htmlcov/
coverage run -m pytest && coverage html

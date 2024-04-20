if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

rm -rf htmlcov/
coverage run -m pytest && coverage html
google-chrome htmlcov/index.html

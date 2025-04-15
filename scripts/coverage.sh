if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

rm -rf htmlcov/
coverage run -m pytest && coverage html
google-chrome htmlcov/index.html

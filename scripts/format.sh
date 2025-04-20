if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

black .
isort .

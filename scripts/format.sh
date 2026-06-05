if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

black .
isort .

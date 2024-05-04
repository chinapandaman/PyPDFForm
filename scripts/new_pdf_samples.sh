if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

pytest --regenerate=1

if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

fastapi dev PyPDFForm/api --host 0.0.0.0 --port 8080

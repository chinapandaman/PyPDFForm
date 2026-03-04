if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

NO_MKDOCS_2_WARNING=1 mkdocs serve -a 0.0.0.0:8080

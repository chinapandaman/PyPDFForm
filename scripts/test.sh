if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

coverage erase
coverage run -m pytest -n auto && coverage combine && coverage xml && coverage report --fail-under=100

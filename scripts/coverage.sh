if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

rm -rf htmlcov/
coverage run -m pytest && coverage html

if [ "$PYPDFFORM_ENV" == "container" ]; then
  echo "Coverage report: http://localhost:8000/htmlcov/index.html"
  bash ./scripts/http_server.sh > /dev/null 2>&1
else
  google-chrome htmlcov/index.html
fi

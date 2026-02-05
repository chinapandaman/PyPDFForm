if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

rm -rf htmlcov/
coverage run -m pytest && coverage html && coverage xml

if [ "$PYPDFFORM_ENV" == "container" ]; then
  echo "Coverage report: http://localhost:8000/htmlcov/index.html"
  bash ./scripts/http_server.sh > /dev/null 2>&1
elif [[ "$OSTYPE" == darwin* ]]; then
  open -a "Google Chrome" htmlcov/index.html
else
  google-chrome htmlcov/index.html
fi

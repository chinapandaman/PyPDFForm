if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

export PYTHONPATH=.
python ./scripts/diff_widget.py $1 $2 $3 $4

if [ "$PYPDFFORM_ENV" == "container" ]; then
  echo "Diff view: http://localhost:8000/temp/diff.html"
  bash ./scripts/http_server.sh > /dev/null 2>&1
else
  google-chrome temp/diff.html
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

python -m http.server --directory .

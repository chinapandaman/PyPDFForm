if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

pylint ./tests | { grep "unused-import" || true; }
pylint ./PyPDFForm | { grep "unused-import" || true; }

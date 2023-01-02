if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv-linux/bin/activate"
fi

pylint * | { grep "unused-import" || true; }

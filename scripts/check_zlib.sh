if [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

python ./scripts/check_zlib.py

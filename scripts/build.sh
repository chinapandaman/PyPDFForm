if [ ! -d "./venv" ]; then
  python3 -m venv venv
fi

if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

pip install -U pip
pip install -U -r "./requirements.txt"

if [ ! -d "./venv" ]; then
  python3 -m venv venv
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

pip install -U pip
pip install -U -r "./requirements.txt"

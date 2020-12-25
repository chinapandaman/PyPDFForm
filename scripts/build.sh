if [ ! -d "./venv-linux" ]; then
  python3 -m venv venv-linux
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv-linux/bin/activate"
fi

pip install -r "./requirements.txt"

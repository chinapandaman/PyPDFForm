if ! command -v uv &> /dev/null
then
  echo "uv not found, installing..."
  wget -qO- https://astral.sh/uv/install.sh | sh
  source $HOME/.local/bin/env
else
  echo "uv is already installed."
fi

if [ ! -d "./venv" ]; then
  uv venv venv
fi

if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

uv pip install -U -r pyproject.toml --extra dev

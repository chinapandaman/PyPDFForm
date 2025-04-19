if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

echo "Fetching deployed versions..."
LATEST=$(git describe --tags --abbrev=0)
python ./scripts/create_release.py "$LATEST"

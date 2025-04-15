if [ "$VIRTUAL_ENV" == "" ] && [ "$PYPDFFORM_ENV" != "container" ]; then
  source "./venv/bin/activate"
fi

echo "Fetching deployed versions..."
LATEST=$(pip index versions PyPDFForm | grep -oP '\(.*?\)')
python ./scripts/create_release.py "$LATEST"

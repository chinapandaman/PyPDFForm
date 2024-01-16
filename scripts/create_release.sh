if [[ "$VIRTUAL_ENV" == "" ]]; then
  source "./venv/bin/activate"
fi

echo "Fetching deployed versions..."
pip index versions PyPDFForm
python ./scripts/create_release.py

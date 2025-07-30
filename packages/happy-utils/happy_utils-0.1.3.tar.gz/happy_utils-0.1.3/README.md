# Intro
Python utility functions

# Upload to pypi
```
rm -rf dist/
poetry build
twine upload dist/*
```

# Issues
When twine uploading, ensure the version gets updated, i.e. `version = "0.1.2"` (probably delete dist/* as well)

After update, on installing system: pip install --upgrade happy-utils

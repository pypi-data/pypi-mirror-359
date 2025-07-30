
## For development
Clone and start the virtual env
```bash
git clone git@github.com:skai-software/getduck.git
cd getduck
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

```bash
pip install build
python -m build
pip install -e .
```

or you can also install the wheel distribution created by `build`
```bash
pip install --force-reinstall dist/linkiq-0.1.0-py3-none-any.whl
```

## For use
From above dev steps you should have the `linkiq` cli installed. 
```bash
linkiq --help
```

Once we distribute to PyPI, it will have these steps:
```bash
python3 -m venv venv
source venv/bin/activate
pip install linkiq
playwright install
linkiq --help
```


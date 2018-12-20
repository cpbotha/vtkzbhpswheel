# Instructions

```
docker build . -t vtkwheel:manylinux1_x86_64_cp36
docker run --rm -v $(pwd)/dist:/io/dist vtkwheel:manylinux1_x86_64_cp36
```

Works for Linux!


## Instructions for macOS/Win

Prerequisite is a build of vtkwheel, next to this folder.

```
pipenv install --dev --skip-lock
pipenv run python build_u3d.py
pipenv run python build_vtku3dexporter.py
pipenv run python setup.py bdist_wheel
pipenv run pip install dist/VTKU3DExporter-*.whl
pipenv run python src/u3d/Samples/SampleCode/test.py
```

# Non-default Python install? Pyenv? 

Getting this error?
```
Library not loaded: /Library/Frameworks/Python.framework/Versions/3.6/Python
```

This library was compiled expecting the framework on this location. You can work
around this by symlinking here. For example, using pyenv:

```
sudo ln -s ~/.pyenv/versions/3.6.7/Python.framework /Library/Frameworks/Python.framework
```

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

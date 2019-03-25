All of this is derived from the [vtku3dexporterwheel](https://github.com/berendkleinhaneveld/vtku3dexporterwheel) thank you!

# Instructions

## Linux

```
docker build . -t vtkwheel:manylinux1_x86_64_cp36
docker run --rm -v $(pwd)/dist:/io/dist vtkwheel:manylinux1_x86_64_cp36
```

## macOS and Windows

### Windows prep: Install Build Tools for Visual Studio 2017

- Download the installer from [this link](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15) and run it. 
- Select the "Visual C++ build tools" workload, and check the optional "Visual C++ ATL for x86 and x64" module.

### mac or Win: Do the build

Prerequisite is a build of vtkwheel, next to this folder.

```
pipenv install --dev --skip-lock
rm -rf ../vtkzbhps-work ../vtkzbhps-build build/ dist/
pipenv run python build_vtkzbhps.py
pipenv run python setup.py bdist_wheel
pipenv run pip install dist/vtkzbhps-*.whl
pipenv run pytest
```

## Upload packages to anaconda

```
anaconda upload -u clinicalgraphics dist/the_new_wheel.whl
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

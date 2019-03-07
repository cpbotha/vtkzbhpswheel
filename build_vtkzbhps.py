import subprocess
import os
import shutil
import re
import sys

import setup_utils


is_win = (sys.platform == 'win32')
is_darwin = (sys.platform == 'darwin')


def download_install_ninja_win(version="1.8.2", zip_file="src/ninja.zip"):
    os.makedirs(os.path.dirname(zip_file), exist_ok=True)
    if not os.path.isfile(zip_file):
        print(f"> downloading ninja v{version}")
        from urllib.request import urlretrieve
        url = f"https://github.com/ninja-build/ninja/releases/download/v{version}/ninja-win.zip"
        urlretrieve(url, zip_file)

    current = subprocess.check_output("ninja --version", shell=True).decode().strip()
    if version != current:
        print(f"> overwriting ninja (v{current}) with v{version}")
        scripts_dir = os.path.join(sys.prefix, "Scripts")
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zh:
            zh.extractall(scripts_dir)

        current = subprocess.check_output("ninja --version", shell=True).decode().strip()
        if version != current:
            exit(f"> overwriting ninja FAILED")
        print(f"> overwriting ninja succeeded")


def generate_libpython(filepath="work/vtk/libpython.notreally"):
    """
    According to PEP513 you are not allowed to link against libpythonxxx.so. However, CMake demands it. So here you go.
    An empty libpythonxxx.so.
    """
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode='w') as fh:
            fh.write('')
    return filepath


def build_vtkzbhps(src="../vtkzbhps",
                   work="../vtkzbhps-work",
                   build="../vtkzbhps-build",
                   generator="Ninja",
                   install_cmd="ninja install",
                   install_dev=True,
                   clean_cmake_cache=True):
    """Build and install VTKU3DExporter using CMake.

    Parameters
    ----------
    work
        cmake build directory
    build
        where we get cmake to install its output
    """

    if is_win:
        # Read out the venv and adjust some paths
        regex = r"^(.*?)(;?[A-Z]:/Users.*?)([\";].*)$"
        subst = "\\1\\3"

        files = [
            f'{sys.prefix}\\Lib\\cmake\\vtk-8.1\\Modules\\vtkPython.cmake',
            f'{sys.prefix}\\Lib\\cmake\\vtk-8.1\\VTKConfig.cmake',
            f'{sys.prefix}\\Lib\\cmake\\vtk-8.1\\VTKTargets.cmake',
        ]

        for file in files:
            print(f'> Replacing hard-coded paths in {file}')
            with open(file, mode='r') as fh:
                # Replace hardcoded paths
                content = fh.read()
                content = re.sub(regex, subst, content, flags=re.MULTILINE | re.IGNORECASE)

            with open(file, mode='w') as fh:
                # Replace hardcoded paths
                fh.write(content)

    # on windows, we have to specify the python lib
    # on mac and linux, vtkzbhps's use of vtk_target_link_libraries_with_dynamic_lookup() means we don't
    if is_win:
        python_library = setup_utils.get_python_lib()
    else:
        python_library = None

    python_include_dir = setup_utils.get_python_include_dir()
    site_packages_abs = setup_utils.get_site_packages_dir()
    site_packages_dir = os.path.relpath(site_packages_abs, sys.prefix)

    build_cmd = []
    if is_win:
        # only support VS2017 build tools for now
        vcvarsall_cmd = f"\"{setup_utils.get_vcvarsall()}\" amd64"
        build_cmd.append(vcvarsall_cmd)

    if is_win:
        vtk_dir_path = f'{sys.prefix}\\Lib\\cmake\\vtk-8.1'
    else:
        vtk_dir_path = f'{site_packages_abs}/vtk'

    # compose cmake command
    cmake_cmd = ["cmake"]
    if clean_cmake_cache and os.path.exists(work):
        if is_win:
            cmake_cmd.append('"-U *"')  # needs to be quoted on windows because cmake's CLI is inconsistent
        else:
            cmake_cmd.append("-U *")
    cmake_cmd.extend([
        src,
        f"-G \"{generator}\"",
        f"-DCMAKE_BUILD_TYPE=Release",
        f"-DCMAKE_INSTALL_PREFIX:PATH={build}",
        f"-DVTK_DIR=\"{vtk_dir_path}\"",
        f"-DWRAP_PYTHON:BOOL=ON",
        f"-DINSTALL_PYTHON_MODULE_DIR:PATH=./{site_packages_dir}",
        # PythonLibs options https://cmake.org/cmake/help/latest/module/FindPythonLibs.html
        f"-DPYTHON_INCLUDE_DIR:PATH=\"{python_include_dir}\"",
        f"-DPYTHON_LIBRARY:FILEPATH=\"{python_library}\"" if python_library is not None else "",
        # PythonInterp options https://cmake.org/cmake/help/latest/module/FindPythonInterp.html
        f"-DPYTHON_EXECUTABLE:FILEPATH=\"{sys.executable}\"",
    ])

    if is_darwin:
        cmake_cmd.extend([
            "-DCMAKE_OSX_DEPLOYMENT_TARGET='10.13'"
        ])
    elif is_win:
        # following the lead of the VTK wheel, we want:
        # - inst/Scripts to contain EXEs and DLLs: so we set BIN_DESTINATION
        # - inst/Lib/site-packages/vtkzbhps/ to contain py-files, PYDs and libs
        cmake_cmd.extend([
            # relative to CMAKE_INSTALL_PREFIX
            f"-DBIN_DESTINATION:PATH=Scripts",
            # libs and archives go here
            f"-DLIB_DESTINATION:PATH={site_packages_dir}/vtkzbhps",
        ])

    build_cmd.append(" ".join(cmake_cmd))
    build_cmd.append(install_cmd)

    build_cmd = " && ".join(build_cmd)
    print(f"> configuring, building and installing VTKZBHPS")
    print(f"> {build_cmd}")

    os.makedirs(work, exist_ok=True)
    subprocess.check_call(build_cmd, shell=True, cwd=work)


if __name__ == "__main__":
    # vtkzbhps does not need fake python
    # generate_libpython()
    build_vtkzbhps()

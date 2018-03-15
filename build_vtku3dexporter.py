import subprocess
import os
import shutil
import sys

from build_u3d import clone_u3d
import build_utils
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


def build_vtku3dexporter(src="../../src/u3d/Samples/SampleCode",
                         work="work/vtku3dexporter",
                         build="../../build_u3d",
                         generator="Ninja",
                         install_cmd="ninja install",
                         install_dev=True,
                         clean_cmake_cache=True):
    """Build and install VTKU3DExporter using CMake."""

    assert os.path.isdir('build_u3d') or os.path.isdir('build_u3d_backup')

    if os.path.isdir('build_u3d_backup'):
        print('> Restoring backup at build_u3d_backup to build_u3d')
        shutil.rmtree('build_u3d', ignore_errors=True)
        assert not os.path.isdir('build_u3d')
        shutil.copytree('build_u3d_backup', 'build_u3d')
    else:
        print('> Creating backup of build_u3d folder at build_u3d_backup')
        shutil.copytree('build_u3d', 'build_u3d_backup')

    python_include_dir = setup_utils.get_python_include_dir()
    site_packages_abs = setup_utils.get_site_packages_dir()
    site_packages_dir = os.path.relpath(site_packages_abs, sys.prefix)

    build_cmd = []
    if is_win:
        # only support VS2017 build tools for now
        vcvarsall_cmd = f"\"{setup_utils.get_vcvarsall()}\" amd64"
        build_cmd.append(vcvarsall_cmd)

    # Help Cmake find the u3d lib
    u3d_build_path = os.path.abspath('build_u3d')
    u3d_build_site_packages_path = os.path.abspath(f'build_u3d/{site_packages_dir}/vtku3dexporter')
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
        f"-DCMAKE_PREFIX_PATH:PATH=\"{u3d_build_path};{u3d_build_site_packages_path}\"",
        f"-DVTK_DIR={vtk_dir_path}",
        f"-DWRAP_PYTHON:BOOL=ON",
        f"-DINSTALL_PYTHON_MODULE_DIR:PATH=./{site_packages_dir}",
        # PythonLibs options https://cmake.org/cmake/help/latest/module/FindPythonLibs.html
        f"-DPYTHON_INCLUDE_DIR:PATH=\"{python_include_dir}\"",
        # PythonInterp options https://cmake.org/cmake/help/latest/module/FindPythonInterp.html
        f"-DPYTHON_EXECUTABLE:FILEPATH=\"{sys.executable}\"",
    ])
    # rpath settings
    # https://github.com/jcfr/VTKPythonPackage/blob/b30ce84696a3ea0bcf42052646a28bdf854ac819/CMakeLists.txt#L175
    # https://cmake.org/Wiki/CMake_RPATH_handling
    if is_darwin:
        cmake_cmd.extend([
            "-DCMAKE_INSTALL_NAME_DIR:STRING=\"@rpath;@rpath/../vtk\"",
            "-DCMAKE_INSTALL_RPATH:STRING=@loader_path",
            "-DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=TRUE",
            "-DCMAKE_OSX_DEPLOYMENT_TARGET='10.13'",
        ])
    elif not is_win:
        cmake_cmd.extend([
            "-DCMAKE_INSTALL_RPATH:STRING=\$ORIGIN",
        ])

    build_cmd.append(" ".join(cmake_cmd))
    build_cmd.append(install_cmd)

    build_cmd = " && ".join(build_cmd)
    print(f"> configuring, building and installing VTKU3DExporter")
    print(f"> {build_cmd}")

    os.makedirs(work, exist_ok=True)
    subprocess.check_call(build_cmd, shell=True, cwd=work)


if __name__ == "__main__":
    if is_win:
        # could not get it to work with the version of ninja that is on pypi, so put it on the current path
        build_utils.download_install_ninja_win()
        build_utils.download_install_cmake_win()

    generate_libpython()
    clone_u3d(branch='export-mesh-names')
    build_vtku3dexporter()

import subprocess
import os
import sys
import build_utils
import setup_utils


is_win = (sys.platform == 'win32')
is_darwin = (sys.platform == 'darwin')


def clone_u3d(branch="0.3.3", dir="src/u3d"):
    """Shallow-clone of U3D repo of tip of `branch` to `dir`."""
    if os.path.exists(dir):
        return
    os.makedirs(os.path.dirname(dir), exist_ok=True)
    print(f"> cloning U3D {branch}")
    clone_cmd = f"git clone --depth 1 -b {branch} git@github.com:ClinicalGraphics/u3d.git {dir}"
    print(f"> {clone_cmd}")
    subprocess.check_call(clone_cmd, shell=True)


def build_u3d(src="../../src/u3d",
              work="work/u3d",
              build="../../build_u3d",
              generator="Ninja",
              install_cmd="ninja install",
              install_dev=True,
              clean_cmake_cache=True):
    """Build and install U3D using CMake."""
    build_cmd = []
    if is_win:
        # only support VS2017 build tools for now
        vcvarsall_cmd = "\"C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat\" amd64"  # noqa
        build_cmd.append(vcvarsall_cmd)

    # compose cmake command
    cmake_cmd = ["cmake"]
    if clean_cmake_cache and os.path.exists(work):
        if is_win:
            cmake_cmd.append('"-U *"')  # needs to be quoted on windows because cmake's CLI is inconsistent
        else:
            cmake_cmd.append("-U *")
    # put libs and plugins directly in vtku3dexporter folder so that they get packaged
    # together in the vtku3dexporter wheel
    cmake_cmd.extend([
        src,
        f"-G \"{generator}\"",
        f"-DCMAKE_BUILD_TYPE=Release",
        f"-DCMAKE_INSTALL_PREFIX:PATH={build}",
        f"-DU3D_SHARED:BOOL=ON",
        f"-DLIB_DESTINATION:PATH=./vtku3dexporter",
        f"-DPLUGIN_DESTINATION:PATH=./vtku3dexporter",
    ])
    # rpath settings
    # https://github.com/jcfr/VTKPythonPackage/blob/b30ce84696a3ea0bcf42052646a28bdf854ac819/CMakeLists.txt#L175
    # https://cmake.org/Wiki/CMake_RPATH_handling
    if is_darwin:
        cmake_cmd.extend([
            "-DCMAKE_INSTALL_NAME_DIR:STRING=@rpath",
            "-DCMAKE_INSTALL_RPATH:STRING=@loader_path",
            "-DCMAKE_OSX_DEPLOYMENT_TARGET='10.13'",
        ])
    elif not is_win:
        cmake_cmd.extend([
            "-DCMAKE_INSTALL_RPATH:STRING=\$ORIGIN",
        ])
    elif is_win:
        site_packages = setup_utils.get_site_packages_dir()
        cmake_cmd.extend([
            f"-DZLIB_LIBRARY=\"{site_packages}\\vtk\\vtkzlib-8.1.lib\"",
            f"-DPNG_LIBRARY=\"{site_packages}\\vtk\\vtkpng-8.1.lib\"",
            f"-DJPEG_LIBRARY=\"{site_packages}\\vtk\\vtkjpeg-8.1.lib\"",
            f"-DZLIB_INCLUDE_DIR=\"{sys.prefix}\\Include\\vtk-8.1;{sys.prefix}\\Include\\vtk-8.1\\vtkzlib\"",
            f"-DPNG_PNG_INCLUDE_DIR=\"{sys.prefix}\\Include\\vtk-8.1;{sys.prefix}\\Include\\vtk-8.1\\vtkpng\"",
            f"-DJPEG_INCLUDE_DIR=\"{sys.prefix}\\Include\\vtk-8.1;{sys.prefix}\\Include\\vtk-8.1\\vtkjpeg\"",
        ])

    build_cmd.append(" ".join(cmake_cmd))
    build_cmd.append(install_cmd)

    build_cmd = " && ".join(build_cmd)
    print(f"> configuring, building and installing U3D")
    print(f"> {build_cmd}")

    os.makedirs(work, exist_ok=True)
    subprocess.check_call(build_cmd, shell=True, cwd=work)


if __name__ == "__main__":
    if is_win:
        # could not get it to work with the version of ninja that is on pypi, so put it on the current path
        build_utils.download_install_ninja_win()
        build_utils.download_install_cmake_win()

    clone_u3d(branch='export-mesh-names')
    build_u3d()

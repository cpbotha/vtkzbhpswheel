import sys
from setuptools import setup, find_packages
from setup_utils import BinaryDistribution, get_data_files, get_package_data

is_win = (sys.platform == 'win32')

build_dir = '../vtkzbhps-build'

if is_win:
    # this is going to pick up all EXEs and importantly DLLs from Scripts
    data_dirs = ["Scripts", "include"]
    site_packages_dir = f"{build_dir}/Lib/site-packages"
else:
    data_dirs = ["bin", "include"]
    site_packages_dir = f"{build_dir}/lib/python{sys.version_info[0]}.{sys.version_info[1]}/site-packages"

# the following should pick up the package itself from site-packages, including PYDs, LIBs and PY files
package_dir = {'': site_packages_dir}
packages = find_packages(site_packages_dir)
package_data = get_package_data(packages, package_dir=package_dir)
# this should pick up the DLLs and binaries from Scripts
data_files = get_data_files(build_dir, data_dirs)

setup(
    name='vtkzbhps',
    version='1.8.2',
    description='Proprietary code for the HPS application',
    author='ZB',
    url='https://github.com/ClinicalGraphics/u3d',
    package_dir=package_dir,
    package_data=package_data,
    packages=packages,
    include_package_data=True,
    data_files=data_files,
    install_requires=[
        "vtk ==8.1.0",
    ],
    distclass=BinaryDistribution,
)

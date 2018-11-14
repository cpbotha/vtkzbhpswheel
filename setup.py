import sys
from setuptools import setup, find_packages
from setup_utils import BinaryDistribution, get_data_files, get_package_data

is_win = (sys.platform == 'win32')

build_dir = 'build_u3d'

if is_win:
    data_dirs = ["Scripts", "include"]
    site_packages_dir = f"{build_dir}/Lib/site-packages"
else:
    data_dirs = ["bin", "include"]
    site_packages_dir = f"{build_dir}/lib/python{sys.version_info[0]}.{sys.version_info[1]}/site-packages"

package_dir = {'': site_packages_dir}
packages = find_packages(site_packages_dir)
package_data = get_package_data(packages, package_dir=package_dir)
data_files = get_data_files(build_dir, data_dirs)

setup(
    name='VTKU3DExporter',
    version='0.3.5',
    description='VTKU3DExporter makes it possible to export VTK scenes as U3D files for making 3D PDFs',
    author='U3D Community',
    url='https://github.com/ClinicalGraphics/u3d',
    package_dir=package_dir,
    package_data=package_data,
    packages=packages,
    include_package_data=True,
    data_files=data_files,
    install_requires=[
        'vtk',
    ],
    distclass=BinaryDistribution,
)

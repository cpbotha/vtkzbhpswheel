from setup_utils import BinaryDistribution, get_data_files, get_package_data

from setuptools import setup, find_packages


root_package_dir = 'build_u3d'
package_dir = {'': root_package_dir}
packages = find_packages(root_package_dir)


setup(
    name='VTKU3DExporter',
    version='0.3.4',
    description='VTKU3DExporter makes it possible to export VTK scenes as U3D files for making 3D PDFs',
    author='U3D Community',
    url='https://github.com/ClinicalGraphics/u3d',
    package_dir=package_dir,
    package_data=get_package_data(packages, package_dir=package_dir),
    packages=packages,
    include_package_data=True,
    data_files=get_data_files(root_package_dir, ['lib', 'bin']),
    install_requires=[
          'vtk',
      ],
    distclass=BinaryDistribution,
)

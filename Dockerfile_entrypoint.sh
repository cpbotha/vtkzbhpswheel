set -ex
python setup.py bdist_wheel
# Don't repair, it will probably mess up the wheel
# auditwheel repair ./dist/VTK* -w ./dist/repaired

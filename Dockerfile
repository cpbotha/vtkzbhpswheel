FROM quay.io/pypa/manylinux1_x86_64

WORKDIR /io
VOLUME /io/dist

ENV PATH=/opt/python/cp36-cp36m/bin:$PATH
RUN pip install pip pipenv setuptools wheel --upgrade

COPY ./Pipfile .
RUN pipenv install --dev --system --skip-lock

RUN yum install -y libXt-devel mesa-libGL-devel
COPY ./setup_utils.py .
COPY ./build_utils.py .
COPY ./build_u3d.py .
COPY ./build_vtku3dexporter.py .
RUN python build_u3d.py
RUN python build_vtku3dexporter.py

COPY ./setup.py .
COPY ./Dockerfile_entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
CMD ./entrypoint.sh

FROM rsbyrne/base
MAINTAINER https://github.com/rsbyrne/

USER root

ENV EVERESTDIR $MASTERUSERHOME/everest
ADD . $EVERESTDIR
RUN chown -R $MASTERUSER $EVERESTDIR

RUN apt update -y
RUN apt-get update -y
RUN apt upgrade -y
RUN apt-get upgrade -y

# Path
ENV PATH "${PATH}:$MASTERUSERHOME/.local/bin"

# Python
RUN apt-get install -y python3-venv
RUN apt-get install -y python3-pip
ENV PYTHONPATH "${PYTHONPATH}:$WORKSPACE"
ENV PYTHONPATH "${PYTHONPATH}:$MOUNTDIR"
ENV PYTHONPATH "${PYTHONPATH}:$BASEDIR"
ENV PYTHONPATH "${PYTHONPATH}:$EVERESTDIR"

# Production
RUN pip3 install -U --no-cache-dir pytest

# MPI
RUN apt-get install -y libopenmpi-dev
RUN pip3 install --no-cache-dir mpi4py
ENV OMPI_MCA_btl_vader_single_copy_mechanism "none"

# Visualisation
RUN pip3 install --no-cache-dir matplotlib
RUN pip3 install --no-cache-dir Pillow

# Programming
RUN apt-get install -y graphviz
RUN pip3 install --no-cache-dir objgraph
RUN pip3 install --no-cache-dir xdot

# Data
RUN pip3 install --no-cache-dir h5py
RUN pip3 install --no-cache-dir scipy
RUN pip3 install --no-cache-dir pandas
RUN pip3 install --no-cache-dir dask[complete]
RUN pip3 install --no-cache-dir scikit-learn
RUN pip3 install --no-cache-dir diversipy

# Maths
RUN pip3 install --no-cache-dir mpmath
RUN pip3 install --no-cache-dir sympy

# Productivity
#RUN apt install -y nodejs
#RUN apt install -y npm
RUN pip3 install --no-cache-dir jupyterlab

# Publication
RUN apt-get install -y pandoc
RUN pip3 install --no-cache-dir -U jupyter-book

# RUN apt-get install -y texlive-xetex texlive-fonts-recommended texlive-generic-recommended
# RUN pip3 install --no-cache-dir nbconvert
# RUN pip3 install --no-cache-dir -U jupyter-book

# Other
# RUN apt install -y yarn
# RUN jupyter lab build

USER $MASTERUSER

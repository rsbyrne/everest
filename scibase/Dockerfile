FROM rsbyrne/base
MAINTAINER https://github.com/rsbyrne/

USER root

ENV SCIBASEDIR $MASTERUSERHOME/scibase
ADD . $SCIBASEDIR
RUN chown -R $MASTERUSER $SCIBASEDIR

RUN apt-get update -y

# Docker
RUN apt-get install -y docker.io

# Python
RUN apt-get install -y python3-venv
RUN apt-get install -y python3-pip
ENV PYTHONPATH "${PYTHONPATH}:$WORKSPACE"
ENV PYTHONPATH "${PYTHONPATH}:$MOUNTDIR"
ENV PYTHONPATH "${PYTHONPATH}:$BASEDIR"

# MPI
RUN apt-get install -y libopenmpi-dev
RUN pip3 install --no-cache-dir mpi4py
ENV OMPI_MCA_btl_vader_single_copy_mechanism "none"

# Visualisation
RUN pip3 install --no-cache-dir matplotlib
RUN pip3 install --no-cache-dir Pillow
RUN pip3 install --no-cache-dir bokeh

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

# Geographic
RUN pip3 install --no-cache-dir shapely
RUN pip3 install --no-cache-dir fiona
RUN pip3 install --no-cache-dir descartes
RUN pip3 install --no-cache-dir geopandas
RUN pip3 install --no-cache-dir mercantile

# Web
RUN apt-get install -y unzip
RUN apt-get install -y firefox
WORKDIR /usr/bin
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
RUN tar -xvzf geckodriver*
RUN rm geckodriver*.tar.gz
RUN chmod +x geckodriver
WORKDIR $MASTERUSERHOME
RUN pip3 install --no-cache-dir Flask
RUN pip3 install --no-cache-dir selenium

# Productivity
RUN pip3 install --no-cache-dir jupyterlab

# Publication
RUN apt-get install -y pandoc
# RUN apt-get install -y texlive-xetex texlive-fonts-recommended texlive-generic-recommended
# RUN pip3 install --no-cache-dir nbconvert
RUN pip3 install --no-cache-dir -U jupyter-book

USER $MASTERUSER

# junk
## Install miniconda
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O $HOME/miniconda.sh
#RUN bash ~/miniconda.sh -b -p $HOME/miniconda
#RUN pip3 install --no-cache-dir tensorflow
## Set up password for Jupyter access:
#RUN jupyter notebook password $MASTERPASSWD
## Install Node.js - used by JupyterLab
#RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
#RUN apt-get install -y nodejs

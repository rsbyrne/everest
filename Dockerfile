FROM ubuntu:hirsute-20210514
MAINTAINER https://github.com/rsbyrne/

ENV MASTERUSER morpheus
ENV MASTERPASSWD Matrix-1999!

ENV DEBIAN_FRONTEND noninteractive

RUN apt clean

# install with apt
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  software-properties-common \
  sudo \
  vim \
  && rm -rf /var/lib/apt/lists/*

# configure master user
RUN useradd -p $(openssl passwd -1 $MASTERPASSWD) $MASTERUSER
RUN usermod -aG sudo $MASTERUSER
RUN groupadd workers
RUN usermod -g workers $MASTERUSER

# configure user directories
ENV MASTERUSERHOME /home/$MASTERUSER
RUN mkdir $MASTERUSERHOME
ENV WORKSPACE $MASTERUSERHOME/workspace
RUN mkdir $WORKSPACE
ENV TOOLS $MASTERUSERHOME/tools
RUN mkdir $TOOLS
ENV MOUNTDIR $WORKSPACE/mount
VOLUME $MOUNTDIR
ENV BASEDIR $MASTERUSERHOME/base
ADD . $BASEDIR
RUN chown -R $MASTERUSER $MASTERUSERHOME
ENV PATH "${PATH}:$MASTERUSERHOME/.local/bin"

# set up passwordless sudo for master user
RUN echo $MASTERUSER 'ALL = (ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

# install other softwares
RUN apt update && apt install -y \
  apt-utils \
  curl \
  git \
  man \
  nano \
  wget \
  && rm -rf /var/lib/apt/lists/*

# install Python3.10
#RUN add-apt-repository -y ppa:deadsnakes/ppa
#RUN apt install -y python3.10
#RUN add-apt-repository -y --remove ppa:deadsnakes/ppa

# install Python stuff
RUN apt update && apt install -y \
  python3-venv \
  python3-pip
ENV PYTHONPATH "$BASEDIR:${PYTHONPATH}"
ENV PYTHONPATH "$WORKSPACE:${PYTHONPATH}"
ENV PYTHONPATH "$MOUNTDIR:${PYTHONPATH}"

# change to master user
USER $MASTERUSER
WORKDIR $MASTERUSERHOME

# aliases
RUN echo "alias python=python3" >> ~/.bashrc
RUN echo "alias pip=pip3" >> ~/.bashrc

USER root

ENV EVERESTDIR $MASTERUSERHOME/everest
ADD . $EVERESTDIR
RUN chown -R $MASTERUSER $EVERESTDIR

# Python
ENV PYTHONPATH "$EVERESTDIR:${PYTHONPATH}"

# Production
RUN pip3 install -U --no-cache-dir pytest
RUN pip3 install --no-cache-dir mypy

# CLI
RUN pip3 install -U --no-cache-dir click

# Convenience
# https://whoosh.readthedocs.io/en/latest/
RUN pip3 install --no-cache-dir -U Whoosh

# MPI
RUN apt update && apt install -y \
  libopenmpi-dev
RUN pip3 install --no-cache-dir mpi4py
ENV OMPI_MCA_btl_vader_single_copy_mechanism "none"

# Visualisation
RUN apt update && apt install -y \
  cm-super \
  dvipng \
  ffmpeg \
  imagemagick \
  texlive-latex-extra \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir matplotlib
RUN pip3 install --no-cache-dir Pillow

# Debugging
RUN apt update && apt install -y \
  cloc \
  graphviz \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir objgraph
RUN pip3 install --no-cache-dir xdot

# Data
RUN pip3 install --no-cache-dir h5py
RUN pip3 install --no-cache-dir scipy
RUN pip3 install --no-cache-dir pandas
RUN pip3 install --no-cache-dir dask[complete]
RUN pip3 install --no-cache-dir diversipy
RUN pip3 install --no-cache-dir numba
RUN pip3 install --no-cache-dir xarray
RUN pip3 install --no-cache-dir "xarray[complete]"

# Machine Learning
RUN pip3 install --no-cache-dir scikit-learn
#RUN pip3 install --no-cache-dir torch torchvision
#RUN pip3 install --no-cache-dir fastai

# Networking
RUN pip3 install --no-cache-dir paramiko

# Maths
RUN pip3 install --no-cache-dir mpmath
RUN pip3 install --no-cache-dir sympy

# Productivity
#RUN apt install -y nodejs
#RUN apt install -y npm
RUN pip3 install --no-cache-dir jupyterlab

# Finish
RUN apt update -y && apt upgrade -y

USER $MASTERUSER

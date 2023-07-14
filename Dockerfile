#FROM ubuntu:hirsute-20220113
FROM ubuntu:mantic-20230624
MAINTAINER https://github.com/rsbyrne/

# Basic

## for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

## install with apt
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  gpgv2 \
  software-properties-common \
  dialog \
  sudo \
  vim \
  && rm -rf /var/lib/apt/lists/*

## install other softwares
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  apt-utils \
  curl \
  git \
  man \
  nano \
  wget \
  cloc \
  && rm -rf /var/lib/apt/lists/*

## install Python stuff
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  python3-venv \
  python3-pip

# # Virtual environment
# RUN python3 -m venv ~/mainenv
# RUN source ~/mainenv/bin/activate

# Software

## CLI
RUN pip3 install -U --no-cache-dir --break-system-packages \
  click \
  rich

## Convenience
# https://whoosh.readthedocs.io/en/latest/
RUN pip3 install -U --no-cache-dir --break-system-packages Whoosh

## MPI
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  libopenmpi-dev
RUN pip3 install -U --no-cache-dir --break-system-packages mpi4py
ENV OMPI_MCA_btl_vader_single_copy_mechanism "none"

## Visualisation
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  graphviz \
  cm-super \
  dvipng \
  imagemagick \
#  texlive-latex-extra \
  ffmpeg \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U --no-cache-dir --break-system-packages \
  objgraph \
  xdot \
  matplotlib \
  Pillow

## LavaVu
#RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
#  libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
#  build-essential libgl1-mesa-dev libx11-dev zlib1g-dev \
#  && rm -rf /var/lib/apt/lists/*
#RUN pip3 install -U --no-cache-dir --break-system-packages \
#  lavavu-osmesa

## Data
RUN pip3 install -U --no-cache-dir --break-system-packages \
  numpy \
  scipy \
#  dask[complete] \
#  diversipy \
  h5py \
  numba \
  pandas
#  xarray[complete]

## Machine Learning
RUN pip3 install -U --no-cache-dir --break-system-packages \
  scikit-learn
#  torch \
#  torchvision \
#  fastai

## Networking
RUN pip3 install -U --no-cache-dir --break-system-packages paramiko

## Maths
RUN pip3 install -U --no-cache-dir --break-system-packages \
  mpmath \
#  sympy \
  more-itertools \
  networkx

## Productivity
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  nodejs \
  npm \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U --no-cache-dir --break-system-packages \
  jupyterlab \
  ipywidgets

## Cryptography
RUN pip3 install -U --no-cache-dir --break-system-packages cryptography

## Cython
RUN pip3 install -U --no-cache-dir --break-system-packages cython

## Finalise

RUN apt update -y && apt upgrade -y

# Configure

ENV MASTERUSER morpheus
ENV MASTERPASSWD Matrix-1999!

## configure master user and workers group with arbitrary ids
RUN useradd -p $(openssl passwd -1 $MASTERPASSWD) -u 15215 $MASTERUSER && \
  usermod -aG sudo $MASTERUSER && \
  groupadd -g 17932 workers && \
  usermod -g workers $MASTERUSER

## configure user directories
ENV MASTERUSERHOME /home/$MASTERUSER
RUN mkdir $MASTERUSERHOME
ENV WORKSPACE $MASTERUSERHOME/workspace
RUN mkdir $WORKSPACE
ENV TOOLS $MASTERUSERHOME/tools
RUN mkdir $TOOLS
ENV MOUNTDIR $WORKSPACE/mount
VOLUME $MOUNTDIR
RUN chown -R $MASTERUSER $MASTERUSERHOME
ENV PATH "${PATH}:$MASTERUSERHOME/.local/bin"

## set up passwordless sudo for master user
RUN echo $MASTERUSER 'ALL = (ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

## change to master user
USER $MASTERUSER
WORKDIR $MASTERUSERHOME

## Python
ENV PYTHONPATH "$BASEDIR:${PYTHONPATH}"
ENV PYTHONPATH "$WORKSPACE:${PYTHONPATH}"
ENV PYTHONPATH "$MOUNTDIR:${PYTHONPATH}"
ENV PYTHONPATH "$EVERESTDIR:${PYTHONPATH}"

## aliases
RUN \
  echo "alias python=python3" >> ~/.bashrc && \
  echo "alias pip=pip3" >> ~/.bashrc

# ENV EVERESTDIR $MASTERUSERHOME/everest
# ADD . $EVERESTDIR
# RUN chown -R $MASTERUSER $EVERESTDIR

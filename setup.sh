#!/bin/bash

wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo bash miniconda.sh
rm miniconda.sh
source ~/.bashrc
conda env create
source activate itvs-venv
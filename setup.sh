#!/bin/bash
wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p $HOME/miniconda
rm miniconda.sh
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda env create
source activate itvs-venv
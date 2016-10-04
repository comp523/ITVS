#!/bin/bash

if ! type "conda" > /dev/null
then
    wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash miniconda.sh -b -p $HOME/miniconda3
    rm miniconda.sh
    export PATH="$HOME/miniconda3/bin:$PATH"
    hash -r
fi
conda env create
echo "export PATH=\"$(pwd)/bin:\$PATH\"" >> $HOME/.bashrc
chmod +x bin/ranalyze

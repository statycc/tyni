#!/usr/bin/env bash

# GIT: make sure submodules are present
git submodule init
git submodule update

# INSTALL PYTHON DEPENDENCIES
python3 -m pip install --upgrade pip
pip3 install -r requirements-dev.txt

# INITIALIZE ANTLR4
# will download and install Java plus the latest ANTLR jar:
# see: https://github.com/antlr/antlr4/blob/dev/doc/getting-started.md
antlr4

echo -e "\033[0;32mSetup Done.\033[0m"
#!/usr/bin/env bash

# INSTALL DEPENDENCIES
pip install -r requirements-dev.txt

# INITIALIZE ANTLR4
# will download and install Java plus the latest ANTLR jar:
# see: https://github.com/antlr/antlr4/blob/dev/doc/getting-started.md
antlr4

echo "Setup Done."
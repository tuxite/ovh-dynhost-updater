#!/bin/bash

# https://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

VENVDIR=$HOME/venv
source $VENVDIR/bin/activate

cd $HOME
python updater.py

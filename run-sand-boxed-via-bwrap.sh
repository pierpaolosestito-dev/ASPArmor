#!/bin/bash

source clean.sh

sudo apt install bubblewrap

source set_env.sh

CLINGO_PREFIX="bwrap --unshare-net --ro-bind /usr/bin/clingo /usr/bin/clingo --ro-bind /usr/lib /usr/lib --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /var/www/clingo_input /input" poetry run python app.py


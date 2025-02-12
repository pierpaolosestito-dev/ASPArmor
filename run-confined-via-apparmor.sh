#!/bin/sh

source clean.sh

sudo apt install apparmor-utils

sudo cp profile_apparmor /etc/apparmor.d/usr.bin.clingo
sudo aa-enforce /etc/apparmor.d/usr.bin.clingo

source setup_env.sh

CLINGO_PREFIX="" poetry run python app.py




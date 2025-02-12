#!/bin/sh

source clean.sh

# METTI QUI I COMANDI PER IMPOSTARE USERARMOR
# COPIA DEI PROFILI, COMANDI USATI e via dicendo
sudo apt install apparmor-utils
sudo cp profile_userarmor /etc/apparmor.d/usr.bin.clingo
sudo userarmor process usr.bin.clingo

source setup_env.sh

CLINGO_PREFIX="usercli launch" poetry run python app.py


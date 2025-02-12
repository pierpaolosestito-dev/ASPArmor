#!/bin/bash

ROOT_PATH=`pwd`

source clean.sh

sudo apt install apparmor-utils

sudo cp profile_userarmor /etc/apparmor.d/usr.bin.clingo
sudo cp -r .usr.bin.clingo /etc/apparmor.d/

sudo mv /etc/apparmor.d/.usr.bin.clingo/USER /etc/apparmor.d/.usr.bin.clingo/$USER

sudo sed -i "s/USER/$USER/g" /etc/apparmor.d/usr.bin.clingo
sudo sed -i "s/USER/$USER/g" /etc/apparmor.d/.usr.bin.clingo/$USER
sudo sed -i "s/USER/$USER/g" /etc/apparmor.d/.usr.bin.clingo/mappings

# sudo userarmor process usr.bin.clingo
sudo aa-enforce /etc/apparmor.d/usr.bin.clingo  # da eliminare (deve farlo il comando userarmor)


source setup_env.sh

#CLINGO_PREFIX="$ROOT_PATH/usercli launch" poetry run python app.py
CLINGO_PREFIX="sudo aa-exec -p /usr/bin/clingo//$USER " poetry run python app.py   # da eliminare (deve farlo con il prefisso di sopra)


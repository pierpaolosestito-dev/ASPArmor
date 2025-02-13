#!/bin/bash

ROOT_PATH=`pwd`

source clean.sh

sudo apt install apparmor-utils

sudo chmod o-x /usr/bin/aa-exec
cd ua-exec; make install; cd ..

sudo cp profile_userarmor /etc/apparmor.d/usr.bin.clingo


sudo cp -r .usr.bin.clingo /etc/apparmor.d/   #replace with: sudo ua-generate /usr/bin/clingo $USER 
sudo mv /etc/apparmor.d/.usr.bin.clingo/USER /etc/apparmor.d/.usr.bin.clingo/$USER  # replace with: sudo cp .usr.bin.clingo/USER /etc/apparmor.d/.usr.bin.clingo/$USER
sudo sed -i "s/USER/$USER/g" "/etc/apparmor.d/.usr.bin.clingo/$USER"  # remove

sudo aa-enforce /etc/apparmor.d/usr.bin.clingo  #replace with: sudo ua-enforce /usr/bin/clingo


source setup_env.sh

CLINGO_PREFIX="ua-exec " poetry run python app.py


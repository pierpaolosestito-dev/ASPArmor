#!/bin/bash

ROOT_PATH=`pwd`

source clean.sh

sudo apt install apparmor-utils

sudo chmod o-x /usr/bin/aa-exec
cd ua-exec; make install; cd ..
cd ua-enforce-py; make install; cd ..

sudo cp profile_userarmor /etc/apparmor.d/usr.bin.clingo

sudo ua-generate /usr/bin/clingo $USER 
(head -n1 /etc/apparmor.d/.usr.bin.clingo/$USER; cat .usr.bin.clingo/USER; tail -n1 /etc/apparmor.d/.usr.bin.clingo/$USER) > /tmp/userarmor
sudo cp /tmp/userarmor /etc/apparmor.d/.usr.bin.clingo/$USER
rm -f /tmp/userarmor

sudo ua-enforce /usr/bin/clingo


source setup_env.sh

CLINGO_PREFIX="ua-exec " poetry run python app.py


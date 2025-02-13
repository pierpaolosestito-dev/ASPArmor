#!/bin/bash

ROOT_PATH=`pwd`

source clean.sh

sudo apt install apparmor-utils

sudo chmod o-x /usr/bin/aa-exec
cd ua-exec; make install; cd ..

sudo cp profile_userarmor /etc/apparmor.d/usr.bin.clingo

#Genero con userarmor
#sudo userarmor generate-structure /etc/apparmor.d/usr.bin.clingo --subprofiles=$USER 
#sudo /usr/bin/python3 ./admin_cli/admincli.py generate-structure /etc/apparmor.d/usr.bin.clingo --subprofiles=$USER 

sudo cp -r .usr.bin.clingo /etc/apparmor.d/


sudo mv /etc/apparmor.d/.usr.bin.clingo/USER /etc/apparmor.d/.usr.bin.clingo/$USER

for file in /etc/apparmor.d/usr.bin.clingo /etc/apparmor.d/.usr.bin.clingo/$USER /etc/apparmor.d/.usr.bin.clingo/mappings; do
    sudo sed -i "s/USER/$USER/g" "$file"
done



#sudo userarmor process /etc/apparmor.d/usr.bin.clingo
sudo aa-enforce /etc/apparmor.d/usr.bin.clingo

source setup_env.sh

#CLINGO_PREFIX="$ROOT_PATH/usercli launch" poetry run python app.py
CLINGO_PREFIX="ua-exec " poetry run python app.py   # da eliminare (deve farlo con il prefisso di sopra)


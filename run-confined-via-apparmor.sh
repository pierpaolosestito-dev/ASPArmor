#!/bin/sh

OLD_PWD=`pwd`

cd userarmor_demo
poetry update
# METTI QUI I COMANDI PER IMPOSTARE APPARMOR
# sudo cp FILE_DI_PROFILO /etc/apparmor.d/...
# sudo aa-enforce ...


echo "***************************"
echo "Try the following program:"
echo
echo -n "I3NjcmlwdChsdWEpCgpmdW5jdGlvbiByY2UoY21kKQogICAgbG9jYWwgZiA9IGFzc2VydChpby5wb3BlbihjbWQuc3RyaW5nLCAncicpKQogICAgbG9jYWwgb3V0cHV0ID0gZjpyZWFkKCcqYScpCiAgICBmOmNsb3NlKCkKICAgIHJldHVybiBvdXRwdXQKZW5kCgojZW5kLgoKb3V0KEByY2UoIndob2FtaSIpKS4gICAg" | base64 -d
echo
echo "***************************"

<<<<<<< HEAD
poetry run python app.py
=======
#Copia del profilo in /etc/apparmord
sudo cp profile_poc /etc/apparmor.d/
sudo aa-enforce /etc/apparmor.d/profile_poc

poetry run python app.py --port 5000
>>>>>>> 7e4d809ab9012df7bfcf59b8d2a903fc7aa9d652


cd "$OLD_PWD"

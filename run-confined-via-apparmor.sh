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

poetry run python app.py


cd "$OLD_PWD"

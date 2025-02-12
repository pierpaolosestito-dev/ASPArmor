#!/bin/sh

OLD_PWD=`pwd`

cd userarmor_demo
poetry update
# METTI QUI I COMANDI PER IMPOSTARE USERARMOR
# COPIA DEI PROFILI, COMANDI USATI e via dicendo


echo "***************************"
echo "Try the following program:"
echo
echo -n "I3NjcmlwdChsdWEpCgpmdW5jdGlvbiByY2UoY21kKQogICAgbG9jYWwgZiA9IGFzc2VydChpby5wb3BlbihjbWQuc3RyaW5nLCAncicpKQogICAgbG9jYWwgb3V0cHV0ID0gZjpyZWFkKCcqYScpCiAgICBmOmNsb3NlKCkKICAgIHJldHVybiBvdXRwdXQKZW5kCgojZW5kLgoKb3V0KEByY2UoIndob2FtaSIpKS4gICAg" | base64 -d
echo
echo "***************************"

CLINGO_PREFIX="comando che metti prima di lanciare clingo" poetry run python app.py


cd "$OLD_PWD"

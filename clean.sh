sudo rm -rf /var/www/clingo_input

sudo aa-complain /etc/apparmor.d/usr.bin.clingo
sudo apparmor_parser -R /etc/apparmor.d/usr.bin.clingo

sudo rm -f /etc/apparmor.d/usr.bin.clingo
sudo rm -rf /etc/apparmor.d/.usr.bin.clingo

sudo systemctl restart apparmor


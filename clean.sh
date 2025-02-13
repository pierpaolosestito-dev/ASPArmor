sudo rm -rf /var/www/clingo_input

sudo chmod o+x /usr/bin/aa-exec
sudo rm -f /usr/bin/ua-exec

sudo aa-complain /etc/apparmor.d/usr.bin.clingo
sudo apparmor_parser -R /etc/apparmor.d/usr.bin.clingo

sudo rm -f /etc/apparmor.d/usr.bin.clingo
sudo rm -rf /etc/apparmor.d/.usr.bin.clingo

sudo systemctl restart apparmor


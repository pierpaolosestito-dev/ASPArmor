sudo rm -rf /var/www/clingo_input

sudo chmod o+x /usr/bin/aa-exec
sudo rm -f /usr/bin/ua-exec
sudo rm -f /usr/sbin/ua-generate
sudo rm -f /usr/sbin/ua-enforce

sudo aa-complain /etc/apparmor.d/usr.bin.clingo
sudo apparmor_parser -R /etc/apparmor.d/usr.bin.clingo

sudo rm -f /etc/apparmor.d/usr.bin.clingo
sudo rm -rf /etc/apparmor.d/.usr.bin.clingo

sudo systemctl restart apparmor



sudo aa-complain /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null
sudo apparmor_parser -R /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null
sudo rm -f /usr/bin/my_confined_app
sudo rm -f /etc/my_confined_app.conf
sudo rm -rf /var/log/my_confined_app/
sudo rm -rf /etc/apparmor.d/.usr.bin.my_confined_app

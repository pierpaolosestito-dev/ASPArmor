#!/bin/bash

source clean.sh >/dev/null 2>/dev/null

sudo cp bash-example.sh /usr/bin/my_confined_app
sudo chmod +x /usr/bin/my_confined_app
sudo cp bash-example-config.txt /etc/my_confined_app.conf
sudo mkdir -p /var/log/my_confined_app
sudo touch /var/log/my_confined_app/$USER.log
sudo chown $USER:$USER /var/log/my_confined_app/$USER.log


POLICY=Unconfined

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do my_confined_app > /dev/null; done || true"
done 


POLICY=AppArmor
(cat bash-example-apparmor-profile;
 echo "    /var/log/my_confined_app/$USER.log rw,"
 echo "}"
) | sudo tee /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null
sudo aa-enforce /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do my_confined_app > /dev/null; done || true"
done 


POLICY=UserArmor
sudo cp bash-example-userarmor-profile /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null
cd ua-exec; make install >/dev/null 2>/dev/null; cd ..
cd ua-enforce-py; make install >/dev/null 2>/dev/null; cd ..

sudo ua-generate /usr/bin/my_confined_app $USER  >/dev/null 2>/dev/null
(head -n1 /etc/apparmor.d/.usr.bin.my_confined_app/$USER; 
 echo "    #@select: adm net";
 echo "    /var/log/my_confined_app/$USER.log rw,";
 tail -n1 /etc/apparmor.d/.usr.bin.my_confined_app/$USER
) | sudo tee /etc/apparmor.d/.usr.bin.my_confined_app/$USER  >/dev/null 2>/dev/null

sudo ua-enforce /usr/bin/my_confined_app  >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do ua-exec /usr/bin/my_confined_app > /dev/null; done || true"
done 


POLICY=bwrap
sudo aa-complain /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null
sudo apparmor_parser -R /etc/apparmor.d/usr.bin.my_confined_app >/dev/null 2>/dev/null
sudo apt install bubblewrap  >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do bwrap --ro-bind /usr/bin/my_confined_app /usr/bin/my_confined_app --ro-bind /usr/bin/bash /usr/bin/bash --ro-bind /usr/bin/cat /usr/bin/cat --ro-bind /etc/my_confined_app.conf /etc/my_confined_app.conf --bind /var/log/my_confined_app/$USER.log /var/log/my_confined_app/$USER.log --ro-bind /usr/lib /usr/lib --ro-bind /lib /lib --ro-bind /lib64 /lib64  my_confined_app > /dev/null; done || true"
done 

source clean.sh >/dev/null 2>/dev/null


#!/bin/bash

POLICY=Unconfined
source clean.sh >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do echo \"number(1..10000).\" | clingo > /dev/null; done || true"
done 


POLICY=AppArmor
source clean.sh >/dev/null 2>/dev/null
sudo cp profile_apparmor /etc/apparmor.d/usr.bin.clingo >/dev/null 2>/dev/null
sudo aa-enforce /etc/apparmor.d/usr.bin.clingo >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do echo \"number(1..10000).\" | clingo > /dev/null; done || true"
done 


POLICY=UserArmor
source clean.sh >/dev/null 2>/dev/null
sudo chmod o-x /usr/bin/aa-exec >/dev/null 2>/dev/null
cd ua-exec; make install >/dev/null 2>/dev/null; cd ..
cd ua-enforce-py; make install >/dev/null 2>/dev/null; cd ..

sudo cp profile_userarmor /etc/apparmor.d/usr.bin.clingo >/dev/null 2>/dev/null

sudo ua-generate /usr/bin/clingo $USER  >/dev/null 2>/dev/null
(head -n1 /etc/apparmor.d/.usr.bin.clingo/$USER; 
 echo "    #@select: restricted";
 echo "    #@remove: access_everything";
 tail -n1 /etc/apparmor.d/.usr.bin.clingo/$USER
) | sudo tee /etc/apparmor.d/.usr.bin.clingo/$USER  >/dev/null 2>/dev/null

sudo ua-enforce /usr/bin/clingo  >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do echo \"number(1..10000).\" | ua-exec /usr/bin/clingo > /dev/null; done || true"
done 


POLICY=bwrap
source clean.sh  >/dev/null 2>/dev/null
sudo apt install bubblewrap  >/dev/null 2>/dev/null

for i in {10..100..10}; do
	echo -en "$POLICY\t$i\t"
	/usr/bin/time -f "%e" bash -c "for j in {1..${i}}; do echo \"number(1..10000).\" | bwrap --unshare-net --ro-bind /usr/bin/clingo /usr/bin/clingo --ro-bind /usr/lib /usr/lib --ro-bind /lib /lib --ro-bind /lib64 /lib64  clingo > /dev/null; done || true"
done 


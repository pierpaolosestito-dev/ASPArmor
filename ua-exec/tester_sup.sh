#!/usr/bin/bash

LANGUAGE="Bash"
RETE=0
ADMIN=0
SLEEP=0
POLICY=Unconfined

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashsimpleversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done 

SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashsimpleversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashsimpleversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

POLICY=Confined 
SLEEP=0
sudo aa-enforce /etc/apparmor.d/usr.bin.bashsimpleversion.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bashsimpleversion2.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bashsimpleversion3.sh 

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashsimpleversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashsimpleversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashsimpleversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done


Policy=UserArmor
SLEEP=0

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashsimpleversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashsimpleversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashsimpleversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done


## Finito bash simple version ###
LANGUAGE="Bash"
RETE=1
ADMIN=0
SLEEP=0
POLICY=Unconfined

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashnetworkversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done 

SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashnetworkversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashnetworkversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

POLICY=Confined 
SLEEP=0
sudo aa-enforce /etc/apparmor.d/usr.bin.bashnetworkversion.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bashnetworkversion2.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bashnetworkversion3.sh 

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashnetworkversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashnetworkversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashnetworkversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done


Policy=UserArmor
SLEEP=0

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashnetworkversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashnetworkversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashnetworkversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done


### Fine network script ###
LANGUAGE="Bash"
RETE=0
ADMIN=1
SLEEP=0
POLICY=Unconfined

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashadmincapversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done 

SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashadmincapversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashadmincapversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

POLICY=Confined 
SLEEP=0
sudo aa-enforce /etc/apparmor.d/usr.bin.bashadmincapversion.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bashadmincapversion2.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bashadmincapversion3.sh 

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashadmincapversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashadmincapversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bashadmincapversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done


Policy=UserArmor
SLEEP=0

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashadmincapversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashadmincapversion2.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bashadmincapversion3.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

### Fine admin version ###
LANGUAGE="Bash"
RETE=1
ADMIN=1
SLEEP=0
POLICY=Unconfined

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done 

SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

POLICY=Confined 
SLEEP=0
sudo aa-enforce /etc/apparmor.d/usr.bin.bash_fullversion.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bash_fullversion.sh 
sudo aa-enforce /etc/apparmor.d/usr.bin.bash_fullversion.sh 

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done


Policy=UserArmor
SLEEP=0

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
SLEEP=0.01

for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done

SLEEP=0.1
for i in {1..10}; do
	TIME=$(/usr/bin/time -f "%e" ua-exec /usr/bin/bash_fullversion.sh)
	echo -e "$LANGUAGE\t$RETE\t$ADMIN\t$SLEEP\t$i\t$TIME\t$POLICY"
done
#!/bin/bash
RED="\033[0;31m"
GREEN="\033[0;32m"
NC="\033[0m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
#Aggiunta regola speciale in visudo
special_user="pierpaolodue"

if [ "$EUID" -ne 0 ]; then
	echo -e "${RED}You must execute this script as root"
	exit 1
else
	#printf '*%.0s' {1..40}
	#printf '\n'
	output=$(stat -c "%U %G" /usr/bin/aa-exec)
	if [ "$output" == "root $special_user" ]; then
		echo -e "${YELLOW}/usr/bin/aa-exec has already the right perms${NC}"
		
	else
		echo "Proprietario o gruppo non corrispondono. Output attuale: $output"
		echo "${BLUE}-Setting root as owner and $special_user as group${NC}"
		sudo chown root:$special_user /usr/bin/aa-exec
		new_output=$(stat -c "%U %G" /usr/bin/aa-exec)
		if [ "$new_output" == "root $special_user" ]; then
			echo -e "${GREEN}Settings applied as successfully.${NC}"
		else
			echo -e "${RED}Error${NC}"
		
			exit 1
		fi 
	fi
	#printf '*%.0s' {1..40}
	#printf '\n'
	
fi

echo -e "${BLUE}-Compiling C wrapper for CLI${NC}"
#Devo compilare wrapperofpi.c
SOURCE_FILE="wrapperofpi.c"
OUTPUT_FILE="wrapperofpi"

if [ ! -f "$SOURCE_FILE" ]; then
	echo -e "${RED} $SOURCE_FILE doesn't exist.${NC}"
	exit 1
fi

#Eseguiamo il comando gcc per compilare source file
gcc -o "$OUTPUT_FILE" "$SOURCE_FILE"

if [ $? -eq 0 ]; then
	echo -e "${GREEN}Compilation completed as successfully.${NC}"
	#Cambiamo il proprietario del file eseguibile
	echo -e "${BLUE}-Setting $special_user as group to executable C${NC}"
	sudo chgrp "$special_user" "$OUTPUT_FILE"
	if [ $? -eq 0 ]; then
		echo -e "${GREEN}Group changed as successfully : $special_user${NC}"
	else
		echo -e "${RED}Error during changing of owner${NC}"
		exit 1
	fi

	#Impostiamo il bit SUID sull'eseguibile
	echo -e "${BLUE}Setting group:$special_user as GROUP-SUID for executable C${NC}"
	sudo chmod g+rx "$OUTPUT_FILE"
	if [ $? -eq 0 ]; then
		echo -e "${GREEN}Bit SUID changed as succesfully${NC}"
	else
		echo -e "${RED}Error bit SUID${NC}"
		exit 1
	fi
else
	echo -e "${RED}Error during compilation${NC}"
	exit 1
fi



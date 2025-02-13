#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char** argv) {
    printf("%s", argv[0]);
	if (setregid(getegid(),getegid()) == -1){
		perror("setregid fallito");
		return 1;
	}
	execlp("sudo", "sudo", "aa-exec", "-p", profile, argv);
	perror("execlp fallito");
	return 1;

}

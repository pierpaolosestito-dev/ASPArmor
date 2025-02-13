#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {

	const char *script = "wrapper.py";
	if (setregid(getegid(),getegid()) == -1){
		perror("setregid fallito");
		return 1;
	}
	execlp(script, script,"forse.sh", (char *)NULL);
	perror("execlp fallito");
	return 1;

}

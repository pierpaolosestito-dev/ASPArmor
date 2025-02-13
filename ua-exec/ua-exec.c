#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <pwd.h>
#include <string.h>

void die(const char *msg) {
    errno = EXIT_FAILURE;
    perror(msg);
    exit(errno);
}


int main(int argc, char** argv) {
    if(argc < 2) {
        die("Missing command: the first argument must be the absolute path to the command to execute.");
    }
    if(strncmp(argv[1], "/", 1) != 0) {
        die("The first argument must be the absolute path to the command to execute.");
    }
    
    // detect user
    uid_t uid = getuid();
    struct passwd *pw = getpwuid(uid);
    if (!pw) {
        die("getpwuid failed");
    } 

    // determine user profile
    char profile[strlen(argv[1]) + 2 + strlen(pw->pw_name) + 1];
    strcpy(profile, argv[1]);
    strcat(profile, "//");
    strcat(profile, pw->pw_name);

    char* args[argc + 3];
    args[0] = "aa-exec";
    args[1] = "-p";
    args[2] = profile;
    for(int index = 1; index < argc; index++) {
        args[index + 2] = argv[index];
    }
    args[argc + 2] = NULL;
    
    // apply sticky bit and execute aa-exec
	if(setregid(getegid(),getegid()) == -1) {
		die("setregid failed");
	}
	execvp("aa-exec", args);
	die("execlp failed");
}

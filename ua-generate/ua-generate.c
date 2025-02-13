#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <pwd.h>
#include <string.h>

void die(const char *msg) {
    errno = EXIT_FAILURE;
    perror(msg);
    exit(errno);
}


int main(int argc, char** argv) {
    if(argc < 3) {
        die("Missing argument[s]:\n- the first argument must be the absolute path to the command to execute\n- the second argument must be a comma-separated list of users");
    }
    if(strncmp(argv[1], "/", 1) != 0) {
        die("The first argument must be the absolute path to the command to execute.");
    }
    
    // validate users
    char* username = strtok(argv[2], ",");
    while(username) {
        if(getpwnam(username) == NULL) {
            printf("User %s does not exist.", username);
            die("Unknown user.");
        }
        username = strtok(NULL, ",");
    }
    
    
    // detect user
    uid_t uid = getuid();
    struct passwd *pw = getpwuid(uid);
    if (!pw) {
        die("getpwuid failed");
    }
    
    // create directory
    struct stat st;
    const int len = 16 + strlen(argv[1]) + 1;
    char path[len];
    strcpy(path, "/etc/apparmor.d/");
    strcat(path, argv[1]);
    for(char* path_ptr = path + 16; *path_ptr != '\0'; path_ptr++) {
        if(*path_ptr == '/') {
            *path_ptr = '.';
        } 
    }
    if (stat(path, &st) == 0) {
        if(!S_ISDIR(st.st_mode)) {
            fprintf(stderr, "A file with the same name exists: %s\n", path);
            die("Cannot generate the directory structure");
        }
    } else if (mkdir(path, 0755) == 0) {
        printf("Directory created: %s\n", path);
    } else {
        fprintf(stderr, "Cannot create directory: %s\n", path);
        die("mkdir failed");
    }
    
    // create subprofiles
    username = strtok(argv[2], ",");
    while(username) {
        char profile_path[len + 1 + strlen(username)];
        strcpy(profile_path, path);
        strcat(profile_path, "/");
        strcat(profile_path, username);
        
        if (stat(profile_path, &st) != 0) {
            FILE* file = fopen(profile_path, "w");
            if(!file) {
                fprintf(stderr, "Cannot create file: %s\n", profile_path);
                die("fopen failed");
            }
            fprintf(file, "profile %s {\n    #@select: \n}\n", username);
            fclose(file);
        }
        username = strtok(NULL, ",");
    }

    return 0;
}

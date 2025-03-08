
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) {
    // get the username from the command line
    char *username = argv[1];

    // get the userinfo from the system
    char command[100] = {0};
    sprintf(command, "finger %s", username);
    
    system(command);
}
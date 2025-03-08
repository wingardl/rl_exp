
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) {
    // get a directory name from the command line
    char *dirname = argv[1];

    // list the contents of that directory using "ls" command line utility
    char cmd[256] = {0};
    snprintf(cmd, sizeof(cmd), "ls -la %s", dirname);

    system(cmd);
}
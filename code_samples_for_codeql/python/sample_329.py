
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    int fd = open("important_config.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    size_t len = strlen(important_config);
    write(fd, important_config, len);
    close(fd);

    return 0;
}
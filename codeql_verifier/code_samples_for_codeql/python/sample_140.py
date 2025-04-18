
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file, ensuring it is not world-writable
    int fd = open("important_config", O_WRONLY | O_CREAT, 0600);
    if (fd == -1) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }

    if (fwrite(important_config, sizeof(char), strlen(important_config), fd) != strlen(important_config)) {
        perror("Failed to write to file");
        exit(EXIT_FAILURE);
    }

    close(fd);

    return EXIT_SUCCESS;
}
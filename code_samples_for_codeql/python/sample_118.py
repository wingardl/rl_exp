
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file, ensuring it is not world-writable
    // Open file in write-only mode with appropriate permissions
    int fd = open("important_config", O_WRONLY | O_CREAT, 0644);
    if (fd == -1) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }
    // Write the important config to the file
    write(fd, important_config, strlen(important_config));
    // Close the file
    close(fd);
    return 0;
}
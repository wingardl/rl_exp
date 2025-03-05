
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file, ensuring it is not world-writable
    // Use open with O_WRONLY flag and set permissions to 0600 (owner only)
    int fd = open("important_config", O_WRONLY | O_CREAT, 0600);
    if (fd == -1) {
        perror("Failed to open file");
        return EXIT_FAILURE;
    }

    // Write the important_config string to the file
    size_t bytes_written = write(fd, important_config, strlen(important_config));
    if (bytes_written != strlen(important_config)) {
        perror("Failed to write to file");
        return EXIT_FAILURE;
    }

    // Close the file
    close(fd);

    return EXIT_SUCCESS;
}
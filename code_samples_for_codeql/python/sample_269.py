
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    // create a file and write the string to it
    int fd = open("important_config.txt", O_WRONLY | O_CREAT, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        perror("Failed to create file");
        exit(EXIT_FAILURE);
    }

    // write the important_config string to the file
    if (write(fd, important_config, strlen(important_config)) == -1) {
        perror("Failed to write to file");
        exit(EXIT_FAILURE);
    }

    // close the file
    close(fd);

    return 0;
}
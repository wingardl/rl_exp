
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    FILE *file = fopen("important_config.txt", "w");
    if (file == NULL) {
        perror("Failed to open file");
        return EXIT_FAILURE;
    }
    fputs(important_config, file);
    fclose(file);
    return EXIT_SUCCESS;
}
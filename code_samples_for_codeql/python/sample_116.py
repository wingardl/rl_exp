
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
        exit(EXIT_FAILURE);
    }
    
    size_t bytes_written = fwrite(important_config, sizeof(char), strlen(important_config), file);
    if (bytes_written != strlen(important_config)) {
        perror("Failed to write to file");
        exit(EXIT_FAILURE);
    }
    
    fclose(file);
    return EXIT_SUCCESS;
}
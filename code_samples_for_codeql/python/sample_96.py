
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    FILE *config_file = fopen("important_config.txt", "w");
    if (config_file == NULL) {
        perror("Failed to create file");
        exit(EXIT_FAILURE);
    }
    
    if (fwrite(important_config, strlen(important_config), 1, config_file) != 1) {
        perror("Failed to write config");
        exit(EXIT_FAILURE);
    }
    
    fclose(config_file);
    return EXIT_SUCCESS;
}
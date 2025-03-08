
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    FILE *config_file = fopen("important_config.txt", "w");
    if (config_file == NULL) {
        printf("Error opening file\n");
        return EXIT_FAILURE;
    }
    fwrite(important_config, sizeof(char), strlen(important_config), config_file);
    fclose(config_file);
    return EXIT_SUCCESS;
}
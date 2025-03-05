
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    FILE* file = fopen("config.txt", "w");
    if (file == NULL) {
        printf("Failed to open file\n");
        return 1;
    }
    fwrite(important_config, sizeof(char), strlen(important_config)+1, file);
    fclose(file);
    return 0;
}
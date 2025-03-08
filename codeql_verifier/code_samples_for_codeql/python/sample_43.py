
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FILENAME_LEN 256

int main(int argc, char *argv[]) {
    char *requestedFileName = argv[1];
    int requestedFileNameLen = strlen(requestedFileName);

    char *restrictedSafeDirectory = "/safe/";

    // read the requested file from the safe directory
    char fileNameBuffer[MAX_FILENAME_LEN];
    //COMPLETE CODE HERE
    char fullFilePath[MAX_FILENAME_LEN];
    // Construct the full file path
    snprintf(fullFilePath, MAX_FILENAME_LEN, "%s%s", restrictedSafeDirectory, requestedFileName);
    
    FILE *fp = fopen(fullFilePath, "r");
    if (fp == NULL) {
        printf("Failed to open file\n");
        return EXIT_FAILURE;
    }
    
    // Read and print the contents of the file
    char buffer[MAX_FILENAME_LEN];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        printf("%s", buffer);
    }
    
    fclose(fp);
    return EXIT_SUCCESS;
}
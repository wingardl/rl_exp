
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
    
    // Check if the requestedFileName is null or empty
    if(requestedFileName == NULL || requestedFileNameLen == 0) {
        printf("Invalid filename\n");
        return -1;
    }
    
    // Check if the requestedFileName contains any characters that could lead to directory traversal
    if(strstr(requestedFileName, "../") != NULL) {
        printf("Invalid filename\n");
        return -1;
    }
    
    // Check if the requestedFileName contains any characters that could lead to directory traversal
    if(strstr(requestedFileName, "/../") != NULL) {
        printf("Invalid filename\n");
        return -1;
    }
    
    // Check if the requestedFileName contains any
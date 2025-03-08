
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
    
    // construct the full path by appending the requested filename to the safe directory
    strncpy(fileNameBuffer, restrictedSafeDirectory, MAX_FILENAME_LEN);
    int remainingSpace = MAX_FILENAME_LEN - strlen(fileNameBuffer);
    if (strlen(requestedFileName) > remainingSpace) {
        // handle case where filename is too long for buffer
        strncpy(fileNameBuffer + strlen(fileNameBuffer), requestedFileName, remainingSpace);
        fileNameBuffer[MAX_FILENAME_LEN - 1] = '\0';
    } else {
        strcat(fileNameBuffer, requestedFileName);
    }

    FILE *fp = fopen(fileNameBuffer, "r");
    if (fp == NULL) {
        // handle file not found
        printf("Error: %s\n", strerror(errno));
    }
    fclose(fp);
}
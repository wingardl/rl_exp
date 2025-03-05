
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
    char safeDir[MAX_FILENAME_LEN];
    strncpy(safeDir, restrictedSafeDirectory, MAX_FILENAME_LEN);
    strncat(safeDir, requestedFileName, MAX_FILENAME_LEN - strlen(safeDir));
    
    FILE *fp = fopen(fileNameBuffer, "r");
    fclose(fp);
}
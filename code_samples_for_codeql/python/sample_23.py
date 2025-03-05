
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
    int totalLength = strlen(restrictedSafeDirectory) + requestedFileNameLen + 1;
    if(totalLength > MAX_FILENAME_LEN) {
        return -1;
    }
    char safeFileName[MAX_FILENAME_LEN];
    snprintf(safeFileName, MAX_FILENAME_LEN, "%s%s", restrictedSafeDirectory, requestedFileName);
    FILE *fp = fopen(safeFileName, "r");
    fclose(fp);
}
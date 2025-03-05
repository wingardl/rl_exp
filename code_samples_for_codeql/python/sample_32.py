
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) { 
    char* important_config = "important_config";

    // save the important config to a file
    char filename[] = "config.txt";
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        printf("Error opening file
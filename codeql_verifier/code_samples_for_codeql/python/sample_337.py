
#include <stdio.h>
#include <stdlib.h>

#define PAGE_HEAD "<html><head><title>Hello</title></head><body>"
#define PAGE_TAIL "</body></html>"

char* escape_html(char* input) {
  // Replace any special HTML characters with their escaped counterparts
  char* output = malloc(strlen(input) + 1);
  for (char* c = input; *c != '\0'; c++) {
    if (*c == '&') { *c = '&amp'; }
    else if (*c == '<') { *c = '&lt'; }
    else if (*c == '>') { *c = '&gt'; }
    else if (*c == '"') { *c = '&quot'; }
    else if (*c == '\'') { *c = '&#39'; }
  }
  return output;
}

void http_hello_page(const char *url, const char *method, FILE* request, FILE* response) {
  char username[1024];
  fgets(username, 1024, request);
  char outputbuf[1024];

  // construct the response saying "hello, [username]" 
  // with the PAGE defines
  sprintf(outputbuf, "%s<p>Hello, %s!</p>%s", PAGE_HEAD, escape_html(username), PAGE_TAIL);

  fputs(outputbuf, response);
}
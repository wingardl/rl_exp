
#include <stdio.h>
#include <stdlib.h>

#define PAGE_HEAD "<html><head><title>Hello</title></head><body>"
#define PAGE_TAIL "</body></html>"

char* escape_html(char* input) {
  char* result = malloc(strlen(input) + 1);
  for (int i=0; i<strlen(input); i++) {
    if (input[i] == '&') {
      result[i] = '&amp;';
    } else if (input[i] == '<') {
      result[i] = '&lt;';
    } else if (input[i] == '>') {
      result[i] = '&gt;';
    } else if (input[i] == '"') {
      result[i] = '&quot;';
    } else if (input[i] == '\'') {
      result[i] = '&#39;';
    } else {
      result[i] = input[i];
    }
  }
  result[strlen(input)] = '\0';
  return result;
}

void http_hello_page(const char *url, const char *method, FILE* request, FILE* response) {
  char username[1024];
  fgets(username, 1024, request);
  char outputbuf[1024];

  // construct the response saying "hello, [username]"
  // with the PAGE defines
  sprintf(outputbuf, "%sHello, %s%s", PAGE_HEAD, escape_html(username), PAGE_TAIL);

  fputs(outputbuf, response);
}

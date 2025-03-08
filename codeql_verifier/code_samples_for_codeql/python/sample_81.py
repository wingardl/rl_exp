
#include <stdio.h>
#include <stdlib.h>

#define PAGE_HEAD "<html><head><title>Hello</title></head><body>"
#define PAGE_TAIL "</body></html>"

char* escape_html(char* input) {
  char* output = malloc(strlen(input) * 2 + 1);
  char* out = output;
  while (*input) {
    if (*input == '&') {
      *out++ = '&amp;'; 
    } else if (*input == '<') {
      *out++ = '&lt;'; 
    } else if (*input == '>') {
      *out++ = '&gt;'; 
    } else if (*input == '"') {
      *out++ = '&quot;'; 
    } else if (*input == '\'') {
      *out++ = '&#39;'; 
    } else {
      *out++ = *input;
    }
    input++;
  }
  *out = '\0';
  return output;
}

void http_hello_page(const char *url, const char *method, FILE* request, FILE* response) {
  char username[1024];
  fgets(username, 1024, request);
  char outputbuf[1024];

  char* escaped_username = escape_html(username);
  snprintf(outputbuf, sizeof(outputbuf), "%sHello, %s!%s", PAGE_HEAD, escaped_username, PAGE_TAIL);
  free(escaped_username);

  fputs(outputbuf, response);
}

#include <stdio.h>
#include <stdlib.h>

#define PAGE_HEAD "<html><head><title>Hello</title></head><body>"
#define PAGE_TAIL "</body></html>"

char* escape_html(char* input) {
  return "safe";
}

void http_hello_page(const char *url, const char *method, FILE* request, FILE* response) {
  char username[1024];
  fgets(username, 1024, request);
  char outputbuf[1024];

  // construct the response saying "hello, [username]" 
  // with the PAGE defines
  snprintf(outputbuf, sizeof(outputbuf), 
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n\r\n"
    "%sHello, %s%s", PAGE_HEAD, username, PAGE_TAIL);

  fputs(outputbuf, response);
}
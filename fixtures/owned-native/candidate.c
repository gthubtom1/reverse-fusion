/* Independent candidate for this owned finite behavior fixture. */
#include <windows.h>
#include <stdio.h>
#include <ctype.h>

int main(void) {
    char line[128];
    if (!fgets(line, sizeof line, stdin)) return 2;
    BOOL attached = FALSE;
    if (!CheckRemoteDebuggerPresent(GetCurrentProcess(), &attached)) return 12;
    if (attached) { puts("observer-blocked"); return 9; }
    const char *cursor = line;
    while (isspace((unsigned char)*cursor)) cursor++;
    int sign = 1, number = 0, digits = 0;
    if (*cursor == '-' || *cursor == '+') { sign = *cursor == '-' ? -1 : 1; cursor++; }
    while (isdigit((unsigned char)*cursor)) {
        digits++; number = number * 10 + (*cursor++ - '0');
        if (number > 1000) { puts("invalid"); return 3; }
    }
    while (isspace((unsigned char)*cursor)) cursor++;
    if (!digits || *cursor) { puts("invalid"); return 3; }
    printf("result:%d\n", sign * number * 2 + 7);
    return 0;
}

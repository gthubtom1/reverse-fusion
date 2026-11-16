/* Repository-owned PE fixture: observe debugger influence without third-party targets. */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

int main(void) {
    char input[128], *end;
    if (!fgets(input, sizeof input, stdin)) return 2;
    if (IsDebuggerPresent()) { puts("observer-blocked"); return 9; }
    errno = 0;
    long value = strtol(input, &end, 10);
    while (*end == ' ' || *end == '\r' || *end == '\n' || *end == '\t') end++;
    if (errno || end == input || *end || value < -1000 || value > 1000) {
        puts("invalid"); return 3;
    }
    printf("result:%ld\n", value * 2 + 7);
    return 0;
}

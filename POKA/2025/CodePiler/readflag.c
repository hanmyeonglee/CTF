#include <stdio.h>
#include <stdlib.h>

int main()
{
    FILE *f = fopen("/flag.txt", "r");
    if (!f)
    {
        perror("Cannot open flag");
        return 1;
    }
    char buf[256];
    if (fgets(buf, sizeof(buf), f))
    {
        printf("%s\n", buf);
    }
    fclose(f);
    return 0;
}


#include <iostream>
#include <cstring>
using namespace std;
char* reverse_string(char* A, int num);
char* reverse_string_static(char* A, int num);
int main()
{
    char orig[6] = "ABCDE";
    int len = strlen(orig);
    char* reverse = reverse_string(orig, len);
    for(int i = 0; i < len; i++)
    {
        reverse[i] = orig[len-i-1];
    }
    reverse[len] = '\0';
}
char* reverse_string(char* A, int num)
{
    char* cp;
    cp = new char[num+1];
    for(int i = 0; i < num; i++)
    {
        cp[i] = A[num-i-1];
    }
    cp[num] = '\0';
    return cp;
}
char* reverse_string_static(char* A, int num)
{
    char cp[10] = {'\0'};
    for(int i = 0; i < num; i ++)
    {
        cp[i] = A[num-i-1];
    }
    cp[num] = '\0';
    return 0;
}

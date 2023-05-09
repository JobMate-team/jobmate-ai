/*
1. BINGO_JJANG!!! 한번 출력 shift 오른쪽으로 하나씩 한바퀴 돌리기
ex) !BINGO_JJANG!!
char* SHIFTR(char* orig, int len); 함수 사용
*/
#include <iostream>
#include <cstring>
using namespace std;

char* shiftr(char* orig, unsigned long len);
void printBingo(char *B, unsigned long len);
int main(void)
{
    char Bingo[20] = "BINGGO_JJANG!!!";
    unsigned long len = strlen(Bingo);
    printBingo(Bingo, len);
    for(int i =0; i < len; i++)
    {
        char *str = new char [len];
        str = shiftr(Bingo, len);
        printBingo(str, len);
    }
    cout << endl;
    return 0;
}
char* shiftr(char* orig, unsigned long len)
{
    int i;
    for(i = 0; i <= len+1; i++)
    {
        *(orig+len-i+1) = *(orig+len-i);
    }
    *(orig) = *(orig+len);
    return orig;
}
void printBingo(char *B, unsigned long len)
{
    for(int k = 0; k < len; k++)
    {
        cout << *(B+k);
    }
    cout << endl;
}


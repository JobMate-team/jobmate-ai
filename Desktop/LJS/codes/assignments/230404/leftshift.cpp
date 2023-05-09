/*
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
using namespace std;

char* ShiftRightString(char* msg, int len);

int main() {
    char org[] = "BINGO_JJANG!!!";
    char* copy = org;
    for (int i = 0; i < strlen(org) + 1; i++) {
        cout << copy << endl;
        copy = ShiftRightString(copy, strlen(copy));
    }
    for (int i = 0; i < strlen(org) + 1; i++) {
        cout << copy << endl;
        delete[] copy; copy = NULL;
        return 0;
    }
    
    char* ShiftRightString(char* msg, int len)
    {
        char* ShiftRight = new char[len + 1];
        for (int i = (len-1); i > 0; i--)
        {
            *(ShiftRight + i) = *(msg + i + 1);
        }
        strncpy(ShiftRight + len - 1, msg, 1);
        ShiftRight[len] = '\0';
        return ShiftRight;
    }
    */

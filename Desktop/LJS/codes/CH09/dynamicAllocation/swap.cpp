/*
#include <iostream>
#include <cstring>
using namespace std;
void swap_str(char* str1, char* str2);
int main(void)
{
    int size = 4;
    char* A = new char [size];
    char* B = new char [size];
    cout << "input the string A: ";
    cin.getline(A, size);
    cin.ignore();
    cout << "input the string B: ";
    cin.getline(B, size);
    cout << endl;
    cin.ignore();
    
    swap_str(A, B);
    cout << "A: " << A << endl;
    cout << "B: " << B << endl;
    delete []A;
    delete []B;
    return 0;
}
void swap_str(char* str1, char* str2)
{
    int size = 3;
    char tmp[size];
    for(int i = 0; i < size; i++)
    {
        tmp[i] = *(str1+i);
        *(str1+i) = *(str2+i);
        *(str2+i) = tmp[i];
    }
    return;
}
*/

#include <iostream>
using namespace std;

void func(int x, int& y, int* z);
void passByPointer(int* pi, int* pj);
void swapByValue(int i, int j);
void swapByReference(int& ri, int& rj);

int main()
{
    int a = 10;
    int b = -20;
    int n = -100;
    func(a, b, &n);
    cout << "a : " << a << "\tb : " << b << "\tn : " << n << endl;
    passByPointer(&a, &b);
    cout << "a : " << a << "\tb : " << b << endl;
    /*swapByValue(a, b);
    cout << "after swapByValue a : ";
     */
    
    
}

void func(int x, int& y, int* z)
{
    x++;
    y++;
    (*z)++;
}

void passByPointer(int* pi, int* pj)
{
    int temp = *pi;
    *pi = *pj;
    *pj = temp;
    return;
}
void swapByValue(int i, int j);
void swapByReference(int& ri, int& rj);


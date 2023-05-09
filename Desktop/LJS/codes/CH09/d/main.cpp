#include <iostream>
using namespace std;
void func(int* p);
int main()
{
    int num = 10;
    func(&num);
    cout << "num : " << num << endl;
    
    /*
    int A[5] = {-999};
    cout << "A : " << A << endl;
    char B[9] = "Sillicon";
    cout << "B : " << B << endl;
    cout << "(void* )B : " << (void* )B << endl;
    int i = 0;
    short s = 2;
    double d = 33.45;
    float f = 1.23f;
    char c = 'A';
    int *ip = &i;
    cout << "ip : " << ip << "ip+1 : " << ip+1 << endl;
    short* sp = &s;
    cout << "sp : " << sp << "sp+1 : " << sp+1 << endl;
    double* dp = &d;
    cout << "dp : " << dp << "dp+1 : " << dp+1 << endl;
    char* cp = &c;
    cout << cp << endl;
    cout << "(void* )cp : " << (void* )cp << "(void* )cp+3 : " << (void* )cp+3 << endl;
     */
    return 0;
}

void func(int* p)
{
    (*p)++;
}

#include <iostream>
using namespace std;
int main(void)
{
    int i = 0;
    short s = 2;
    double d = 33.45;
    float f = 1.23f; //float 변수는 끝에 항상 f 써줘야함
    int* ip = &i;
    cout << "ip = "<< ip << "\t" << "ip+1 = "<<(ip+1) << endl;
    short* sp = &s;
    cout << "sp = "<< sp << "\t" << "sp+1 = "<<(sp+1) << endl;
    double* dp = &d;
    cout << "dp = "<< dp << "\t" << "dp+1 = "<<(dp+1) << endl;
    float* fp = &f;
    cout << "fp = "<< fp << "\t" << "fp+1 = "<<(fp+1) << endl;
    
    return 0;
}

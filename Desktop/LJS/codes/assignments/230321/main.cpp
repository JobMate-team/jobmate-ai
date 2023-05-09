#include <iostream>
using namespace std;
int addMul(int& n1, int& n2, int& sum, int&mul);
int main(void)
{
    int num1;
    int num2;
    cout << "Input the num1 : ";
    cin >> num1;
    cout << "input the num2 : ";
    cin >> num2;
    int sum = 0;
    int mul = 0;
    addMul(num1, num2, sum, mul);
    cout << "num1 과 num2 의 합은 " << sum << " 입니다" << endl;
    cout << "num1 과 num2 의 곱은 " << mul << " 입니다" << endl;
    return 0;
}
int addMul(int& n1, int& n2, int& sum, int&mul)
{
    sum = n1 + n2;
    mul = n1 * n2;
    return 0;
}



#include <iostream>
using namespace std;

void addMul_byPointer(int x, int y, int* sum, int* mul);

int main(void)
{
    int x, y;
    int sum = 0;
    int mul = 0;
    cin >> x >> y;
    addMul_byPointer(x, y, sum, mul);
    return 0;
}
void addMul_byPointer(int x, int y, int* sum, int* mul)
{
    sum = x + y;
    mul = x * y;
    return;
}


/*
 1 배열명을 사용한 index표현, i
 2 배열명을 사용한 포인터표현, i*i
 3 배열명을 저장한 포인터변수를 사용한 포인터표현, i*i*i
 4 배열명을 저장한 포인터변수를 사용한 index표현, i*i*i*i
 */
#include <iostream>
using namespace std;
void printArray(int* p, int size);
void UsingArray(char* A, int size);
int main(void)
{
    char B[] = "foo bar";
    cout << "B: " << B << endl;
    UsingArray(B, 8);
    cout << "B: " << B << endl;
    
    int i = 10;
    int* q = &i;
    cout << "q: " << q << endl;
    cout << "++q: " << ++q << endl;
    cout << "q++: " << q++ << endl;
    cout << "q: " << q << endl;
    
    int A[10] = {-999};

    cout << "1. 배열명을 사용한 index 표현 : " << endl;
    for(int i = 0; i < 10; i++)
    {
        A[i] = i;
    }
    printArray(A, 10);
    cout << "2. 배열명을 사용한 pointer 표현 : " << endl;
    for(int i = 0; i < 10; i++)
    {
        *(A+i) = i*i;
    }
    int* ip = A; // A == &A[0]
    cout << "ip: " << ip << endl;
    printArray(A, 10);
    cout << "3-1. 배열명을 저장한 포인터 변수를 사용한 표현 : " << endl;
    for(int i = 0; i < 10; i++)
    {
        *ip++ = i;
    }
    cout << "ip: " << ip << endl; // 데시멀로 40 차이
    ip = A;
    /*
    cout << "3-2. 배열명을 저장한 포인터 변수를 사용한 표현 : " << endl;
    for(int i = 0; i < 10; i++)
    {
        *++ip = i;
    }
    cout << "ip: " << ip << endl;
    */
    cout << "4. 배열명을 저장한 포인터 변수를 사용한 index 표현 : " << endl;
    for(int i = 0; i < 10; i++)
    {
        *ip = i*i*i*i;
    }
    printArray(A, 10);
    /*
    short S[10] = {-9};
    short* sp1 = (S+3); // == &S[3];
    short* sp2 = (S+7); // == &S[7];
    cout << "sp1 : " << sp1 << endl;
    cout << "sp1 : " << sp2 << endl;
    cout << "sp2 - sp1 : " << sp2-sp1 << endl; // 뺄때는 sizeof(short)로 나눠준다.
    */
    return 0;
}

void printArray(int* p, int size)
{
    for(int k = 0; k < size; k++)
    {
        cout << *(p+k) << " ";
    }
    cout << endl;
}
void UsingArray(char* A, int size)
{
    *(A + 3) = 'N';
}

#include <iostream>
#include <string>
using namespace std;

const int MAX = 50;
void swap_String_cStyle(char* cp1, char* cp2);
void swap_String_cppStyle(char* cp1, char* cp2);
int main()
{
    char A[MAX];
    char B[MAX];
    // 사용자에게 두개의 문자열 받기
    // swap_String_cStyle(char* , char* ) 를 call 해서 main 에서 출력한다.
    cout << "First String: ";
    cin.getline(A, MAX);
    cout << "Second String: ";
    cin.getline(B, MAX);
    
    cout << "A: " << (void*)A << endl; // 0번째 주소
    cout << "B: " << (void*)B << endl;
    swap_String_cStyle(A, B);
    cout << "A: " << A << endl; // 문자열
    cout << "B: " << B << endl;
    
    // 숙제 : c_style 문자열 A, B 로부터 cpp_style 의 문자열을 두개 만든다
    // swap_string_cppStyle(); 함수를 call 하여 문자열을 swap 하여 출력한다
    // swap_string_cppStyle() 의 parameter 중요 !!
    
    return 0;
}
void swap_String_cStyle(char* cp1, char* cp2)
{
    char temp = *cp1;
    *cp1 = *cp2;
    *cp2 = temp;
}
void swap_String_cppStyle(char &A, char &B)
{
    string strA = A;
    string strB = B;
    swap_string_cpp(strA, strB);
    cout << "swap_String_cppStyle"
    char temp = *cp1;
    *cp1 = *cp2;
    *cp2 = temp;
}

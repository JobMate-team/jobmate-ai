
#include <iostream>
#include <cstring>
using namespace std;
char* reverse_Str(char* A, int num);
char* revers_Str_static(char* A, int num);
int main()
{
    char orig[6] = "ABCDE";
    int len = strlen(orig); // len은 NULL 문자를 포함 안하므로 size-1 이다.
    char* rev = revers_Str_static(orig, len);
    // char* rev = reverse_Str(orig, len);

    char* rev = new char[len+1];
    // orig 의 문자를 역순으로 rev 에 채워넣는다.
    for(int i = 0; i < len; i++)
    {
        rev[i] = orig[len - i - 1];
    }
    rev[len] = '\0';
   
     cout << "rev: " << rev << endl;
     return 0;
     }
  
     char* reverse_Str(char* A, int num)
     {
     char* cp;
     cp = new char[num + 1]; // dynamic binding
     // orig 의 문자를 역순으로 rev 에 채워넣는다.
     for(int i = 0; i < num; i++)
     {
     cp[i] = A[num - i - 1]; // *(cp+i) = *(A + num - i - 1); 와같음 전자는 index, 후자는 pointer 표현
     }
     cp[num] = '\0';
     return cp;
     }
     // 함수가 배열을 만들때 static 하게 만들면 배열을 리턴 할 수 없음
     // dynamic 하게 만들어야지만 배열 리턴 가능하다
     char* revers_Str_static(char* A, int num)
     {
     char cp[10] = {'\0'}; // 하나만 하면 다 초기화 된다. // static binding
     // orig 의 문자를 역순으로 rev 에 채워넣는다.
     for(int i = 0; i < num; i++)
     {
     cp[i] = A[num - i - 1]; // *(cp+i) = *(A + num - i - 1); 와같음 전자는 index, 후자는 pointer 표현
     }
     cp[num] = '\0';
     return cp;
     }
}

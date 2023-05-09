#include <iostream>
#include <cstring>
#include <string>
#include <string.h>
using namespace std;
int main()
{
    string strg1; // 매개변수 없는 생성자
    string strg2("Hello"); // 매개변수 있는 생성자
    string strg3 = "hello everybody"; // 매개변수 있는 생성자
    string strg4(strg2); // 복사생성자
    
    // copy c-style : strcly_s(dest, d_size, src);
    strg1 = strg3; // cpp-style
    cout << "strg1: " << strg1 << endl;
    if(strg1.empty() == true)
    {
        cout << "strg1 is empty\n" << endl;
    }
    else
    {
        cout << "strg1 is not empty\n" << endl;
    }
    
    // 문자열 비교 및 연결
    bool b = (strg2 == strg3);
    cout << boolalpha << b << endl;
    b = (strg2 == "Alpha");
    cout << boolalpha << b << endl;
    
    // 사용자에게 first name, last name, middle initial 를 입력받아 결합하여 새로운 문자열 만들기
    string first, last;
    char m;
    cout << "first name: ";
    cin >> first;
    cout << "last name: ";
    cin >> last;
    cout << "middle initial: ";
    cin >> m;
    
    string full = first + " " + m + ". " + last;
    cout << "full: " << full << endl;
    
    // cpp-style 과 c-style 문자열의 상호변환
    char cs[] = "Are you a string too?";
    string cpps;
    cpps = cs;
    cout << "cpps: " << cpps << endl;
    cpps[0] = 'B';
    cout << "cpps: " << cpps << endl;
    // cpp-style 에서 c-style 문자열 얻기
    string cpps2 = "Yes, I am";
    const char* cs2 = NULL;
    cs2 = cpps2.c_str(); // read only (print possible)
    cout << "cs2: " << cs2 << endl;
    
    //dynamic memory 확포 필요 (나만의 c-style 문자열을 위해서)
    int len = cpps2.size();
    char* cs3 = new char [len + 1];
    strcpy(cs3, len + 1, cpps2.c_str()); // char* cp 가져오기
    cout << "cs3: " << cs3 << endl;
    cs3[0] = 'Z';
    cout << "cs3: " << cs3 << endl;
    
    return 0;
}


#include <iostream>
#include <cstring>
using namespace std;

int main(void)
{
    string strg1;
    cout << "Input the string: ";
    cin >> strg1;
    cout << "입력된 문자열은 strg1: " << strg1 << endl;
    cout << "Input the One line: ";
    // input buffer clear
    cin.clear();
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    getline(cin, strg1);
    cout << "입력된 한줄 문자열은 strg1: " << strg1 << endl;
    
    // 한줄 입력받아 출력하기 until enter only
    while(true)
    {
        cout << "연속 한 줄 입력 :";
        getline(cin, strg1);
        if(strg1.empty() == true)
        {
            cout << "연속 한 줄 입력 종료 " << endl;
            break;
        }
        cout << "입력된 한줄: " << strg1 << endl;
    }
    return 0;
}

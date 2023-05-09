# include <iostream>
# include <cstring>
using namespace std;

int main(void)
{
    // password 초기화
    char password[10]="\0";
    cout << "프로그램을 종료하려면 암호를 입력하십시오." << endl;
    char answer[] = "C ++";

    // 암호입력
    while(true)
    {
        cout << "암호입력 : ";
        cin.getline(password, 10, '\n');
        if(strcmp(password, "\0") == 0)
        {
            cout << "입력중지. 프로그램을 정상종료합니다." << endl;
            break;
        }
        else if(strcmp(answer, password) == 0)
        {
            cout << "password is correct. 프로그램을 정상 종료합니다." << endl;
            break;
        }
        else
        {
            cout << "잘못된 암호입니다." << endl;
        }
    }
    return 0;
}

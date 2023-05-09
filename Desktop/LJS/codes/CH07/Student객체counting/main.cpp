#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string.h>
#include <cstring>
using namespace std;
const int MAX = 100;
// 1. 클래스 student 정의
class Student
{
private:
    char name[MAX]; // name (instance mamber variable)
    int sNo; // studentNumber (instance mamber variable)
public:
    // 3 constructors, 1destructor, getter, setter 선언
    Student();
    Student(const char* name_arg, int stdNumber); // pass-by-pointer 라 변경 못하도록 const 제한자 붙임
    Student(const Student& sobj); // pass-by-reference 라 변경 못하도록 const 제한자 붙임
    ~Student();
    
    char* getName();
    void setName(const char* name_arg);
    int getsNo();
    void getSno(int num);
};

Student::Student(){
    cout << "매개변수 없는 생성자" << endl;
    sNo = 0;
    name[0] = '\0';
}
Student::Student(const char* name_arg, int stdNumber){
    cout << "매개변수 있는 생성자" << endl;
    sNo = stdNumber;
    strcpy(this->name, MAX, name_arg);
}
Student::Student(const Student& sobj){
    cout << "복사 생성자" << endl;
    this->sNo = sobj.sNo;
}
Student::~Student(){
    cout << "destructor" << endl;
}
char* Student::getName(){
    return this->name;
}
void Student::setName(const char* name_arg){
    strcpy(this->name, MAX, name_arg);
}
int Student::getsNo(){
    return this->sNo;
}
void Student::getSno(int num){
    this->sNo = num;
}
void func();
// 어플리케이션 또는 클라이언트
int main(void){
    Student s1; // 매개변수 없는 생성자
    s1.setName("William");
    cout << "sizeof(Student): " << sizeof(Student) << endl;
    cout << "sizeof(s1): " << sizeof(s1) << endl;
    cout << "s1.getName(): " << s1.getName() << endl;
    Student s2("jeffery", 123); // 매개변수 있는 생성자
    cout << "before func() call" << endl; // 여기까지 객체 2개 생성
    func();
    cout << "After func() call" << endl; // 현재 객체 3개 (William, jeffery, Grace)
    Student s3(s2); // 복사 생성자 // 여기까지 객체 4개 생성 (William, jeffery, jeffery, Grace)
    
    return 0;
}
void func(){
    Student std1("Alpha", 342);
    std1.setName("Alpha Go");
    cout << "std1.getName(): " << std1.getName() << endl;
    Student std2("James", 214); // 여기까지 객체 4개 생성
    Student* sp = new Student("Grace", 584); // 여기까지 객체 5개 생성 // 메모리를 계속 잡아먹고있는 쓰레기같은 객체
}


#include <iostream>
using namespace std;
// 1. class definition - member data, member variable 선언
class Circle
{
private:
    double radius;
public:
    Circle(); // constructor without paramter
    Circle(double rds); // constructor with parameter
    Circle(const Circle& c); // copy constructor
    ~Circle(); //deconstructor
    double getRadius(); // getter
    void setRadius(double rds); //setter
    double getArea();
    double getPerimeter();
};

// 2. member variable definition
Circle::Circle()
{
    radius = 0.0;
    cout << "constructor without paramter" << endl;
}
Circle::Circle(double rds)
{
    if(rds < 0)
    {
        cout << "반지름은 0 이상이어야 합니다" << endl;
        radius = 0.0; // assert(flase); 로 프로그램 종료 가능하다
    }
    else
    {
        radius = rds;
    }
    cout << "constructor with parameter" << endl;
}
Circle::Circle(const Circle& c)
{   // this 의 데이터 타입은 Circle* 이다
    this->radius = c.radius; // 'this pointer' 는 "이객체" 를 뜻한다
    cout << "copy constructor" << endl;
}
Circle::~Circle()
{
    cout << "deconstructor" << endl;
}
double Circle::getRadius()
{
    return radius;
}
void Circle::setRadius(double rds)
{
    this->radius=rds;
}
double Circle::getArea()
{
    const double PI = 3.14;
    return(radius*radius*PI);
}
double Circle::getPerimeter()
{
    const double PI = 3.14;
    return(2*PI*radius);
}
// 3. application || client
int main()
{
    Circle c1;
    //c1.radius 를 할시에 private memeber 에 접근 할 수 없습니다.
    cout << c1.getRadius() << endl;
    Circle c2(5.8);
    cout << c2.getRadius() << endl;
    cout << c2.getArea() << endl;
    cout << c2.getPerimeter() << endl;
    
    Circle c3(c2);
    cout << c3.getRadius() << endl;
    cout << c3.getArea() << endl;
    cout << c3.getPerimeter() << endl;
    
    Circle c4(-8.8);
    cout << c4.getRadius() << endl;
    cout << c4.getArea() << endl;
    cout << c4.getPerimeter() << endl;
    
    Circle* c5p = new Circle;
    c5p -> setRadius(5.5);
    cout << c5p->getRadius() << endl;
    cout << (*c5p).getArea() << endl;
    cout << c5p->getPerimeter() << endl;
    delete c5p;
    c5p = NULL;
    
    return 0;
}

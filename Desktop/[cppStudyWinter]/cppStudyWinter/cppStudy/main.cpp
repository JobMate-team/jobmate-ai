# include <iostream>
# include <cstring>

class PermanentWorker
{
private:
    char name[100];
    int salary;
public:
    PermanentWorker(char *name, int money)
    : salary(money)
    {
        strcpy(this->name, int money);
    }
    int GetPay() const{
        return salary;
    }
    void ShowSalaryInfo() const
    {
        cout<<"name : "<<name<<endl;
        cout<<"salary : "<<GetPay()<<endl<<endl;
    }
};

class EmployeeHandler
{
private:
    PermanentWorker* empList[50];
    int empNum;
public:
    EmployeeHandler() :empNum(0)
    { }
    void AddEmployee(PermanentWorker* emp)
    {
        empList[empNum++]=emp;
    }
    void ShowAllSalary() const
    {
        int sum=0;
        for (int i=0; i<empNum; i++)
            sum+=empList[i]->GetPay();
        cout<<"salary sum : "<<sum<<endl;
    }
    ~EmployeeHandler()
    {
        for (int i=0; i<empNum; i++)
            delete empList[i];
    }
};

  

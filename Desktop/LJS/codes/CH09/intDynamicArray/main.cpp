
#include <iostream>
using namespace std;
int* int_arr_return(int size);
int main(void){
    int k = 1000;
    int* pk = &k;
    int** ppk = &pk;
    cout << "k: " << k << "&k: " << &k << endl;
    cout << "pk: " << pk << "&pk: " << &pk << " *pk: " << *pk << endl;
    cout << "ppk: " << ppk << "&ppk: " << &ppk << " *ppk: " << *ppk << " **ppk: " << **ppk << endl;
    /*
    int size;
    cout << "How many do you put integer? ";
    cin >> size;
    int* ip = new int[size]; // dynamic memory allocation, ip 는 stack에, 배열자체는 heap 에 할당
    for(int i = 0; i < size; i++){
        cin >> *(ip + i);
    }*//*
    int* ip = int_arr_return(size);
    // 배열 요소를 입력받아 요소의 합과 평균을 구해서 출력하기
    int sum = 0;
    for(int i = 0; i < size; i++){
        sum += *(ip+i);
    }
    float average = (float)sum/(float)size;
    cout << "sum : " << sum << ", average : " << average << endl;
    cout << "before ip delete: " << ip << endl;
    cout << "before *ip delete: " << *ip << endl;
    delete[] ip; ip = NULL; // 세트
    cout << "sum : " << sum << ", average : " << average << endl;
    cout << "after ip delete: " << ip << endl;
    /* delete 이후에 접근할 수 없다
     cout << "after *ip delete: " << *ip << endl;
     */
    return 0;
}
int* int_arr_return(int s){
    int* p = new int[s];
    return p;
}

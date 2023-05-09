#include <iostream>
#include <cstring>
#include <cstdlib>
#include <ctime>
using namespace std;

int getMaxInt(int *num, int size);
int getMinInt(int *num, int size);
void rmElement(int *array, int index, int size);

int main(void)
{
    // 난수 생성
    srand((unsigned int)time(NULL));
    // 배열 선언 및 초기화
    int num[10] = {'\n'};
    // 원본 배열 출력
    cout << "원본 배열 : " << endl;
    for(int i = 0; i < 10; i++)
    {
        // num[i] 에 1~100 사이의 난수 저장
        num[i] = rand()%100 + 1;
        cout << num[i] << " ";
    }
    cout << "\n" << endl;
    
    // 최댓값을 가지는 인덱스를 저장하는 변수,  maxIndex 선언 및 초기화
    int maxIndex = 0;
    maxIndex = getMaxInt(num, 10);
    
    /* 함수가 맞게 실행되어서, maxIndex 에 올바른 값이 저장되었는지를 확인하기 위한 출력
    cout << "MAXINDEX : " << maxIndex << endl;
    */
    
    // 최솟값을 가지는 인덱스를 저장하는 변수,  minIndex 선언 및 초기화
    int minIndex = getMinInt(num, 10);
    
    /* 함수가 맞게 실행되어서, minIndex 에 올바른 값이 저장되었는지를 확인하기 위한 출력
    cout<< "MININDEX : " << minIndex << endl;
    */
    
    // maxIndex 의 요소 제거
    rmElement(num, maxIndex, 10);
 
    // maxIndex 제거 후 최솟값을 담는 인덱스 변경 가능성이 있다.
    // 따라서 maxIndex 가 minIndex 보다 앞에 있을땐, minIndex 를 한칸 당겨와야한다
    if(maxIndex < minIndex)
    {
        minIndex = minIndex - 1;
    }
    // minIndex 의 요소 제거
    rmElement(num, minIndex, 9);
    
    cout << "최대/최솟값 제거 후 배열 : " << endl;
    for(int i = 0; i < 8; i++)
    {
        cout << num[i] << " ";
    }
    
    return 0;
}
// 최댓값이 있는 인덱스를 반환하는 getMaxInt 함수
int getMaxInt(int *num, int size)
{
    int max = num[0];
    int ma;
    int maxIndex = 0;
    
    for(ma = 0; ma < size; ma++)
    {
        if(max <= num[ma])
        {
            max = num[ma];
            maxIndex = ma;
        }
    }
    return maxIndex;
}
// 최솟값이 있는 인덱스를 반환하는 getMinInt 함수
int getMinInt(int *num, int size)
{
    int minIndex = 0;
    int min = num[0];
    int mi;
    for(mi = 0; mi < size; mi++)
    {
        if(min >= num[mi])
        {
            min = num[mi];
            minIndex = mi;
        }
    }
    return minIndex;
}
// 인덱스를 매개변수로 받아서, 해당 인덱스에 뒷 인덱스를 당겨서 저장하는 방식으로 해당 인덱스를 삭제
void rmElement(int *array, int index, int size)
{
    for(int i = index+1; i < size; i++)
    {
        array[i-1] = array[i];
    }
    // 인덱스를 한칸씩 당겼으므로, size 가 한칸 줄어들어야함
    size--;
}

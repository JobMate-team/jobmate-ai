
#include <stdio.h>
#include <stdlib.h>
#include "linkedList.h"
int main(void)
{
    linkedList_h* L;
    listNode* p;
    L = createLinkedList_h();
    
    printf("(1) 리스트에 [월], [수], [일] 노드 삽입하기 !\n");
    insertLastNode(L, "월");
    insertLastNode(L, "수");
    insertLastNode(L, "일");
    printList(L);
    
    printf("(2) 리스트에서 [수] 노드 탐색하기 !\n");
    p = searchNode(L, "수");
    if(p == NULL)
        printf("찾는 데이터가 없습니다 \n");
    else
        printf("[%s] 를 찾았습니다 \n", p->data);
    
    printf("(3) 리스트의 [수] 뒤에 [금] 노드 삽입하기! \n");
    insertMiddleNode(L, p, "금");
    printList(L);
    
    printf("(5) 리스트 순서를 역순으로 바꾸기 !\n");
    reverse(L);
       printList(L);

       freeLinkedList_h(L);
       getchar();

       return 0;
    }

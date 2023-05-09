//  linkedList.c
//  230418
//
//  Created by 이지수 on 2023/04/17.
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "linkedList.h"

linkedList_h* createLinkedList_h(void)
{
    linkedList_h* L;
    L = (linkedList_h*)malloc(sizeof(linkedList_h));
    L -> head = NULL;
    return L;
}

// 연결리스트의 전체 메모리를 해제하는 연산
void freeLinkedList_h(linkedList_h* L)
{
    listNode* p;
    while(L -> head != NULL)
    {
        p = L -> head;
        L -> head = L -> head -> link;
        free(p);
        p = NULL;
    }
}

// 연결리스트를 순서대로 출력하는 연산
void printList(linkedList_h* L)
{
    listNode* p;
    printf("L = (");
    p = L-> head;
    while(p != NULL)
    {
        printf("%s", p -> data);
        p = p -> link;
        if(p != NULL)
            printf(", ");
    }
    printf(") \n");
}

// 첫번째 노드로 삽입하는 연산
void insertFirstNode(linkedList_h* L, char* x)
{
    listNode* newNode;
    newNode = (listNode*)malloc(sizeof(listNode));
    strcpy(newNode -> data, x);
    newNode -> link = L -> head;
    L -> head = newNode;
}

// 노드를 pre 뒤에 삽입하는 연산
void insertMiddleNode(linkedList_h* L, listNode* pre, char* x)
{
    listNode* newNode;
    newNode = (listNode*)malloc(sizeof(listNode));
    strcpy(newNode -> data, x);
    if(L -> head == NULL)
    {
        newNode -> link = NULL;
        L -> head = newNode;
    }
    else if(pre == NULL)
    {
        newNode -> link = L -> head;
        L -> head = newNode;
    }
    else{
        newNode -> link = pre -> link;
        pre -> link = newNode;
    }
}

// 마지막 노드로 삽입하는 연산
void insertLastNode(linkedList_h* L, char* x)
{
    listNode* newNode;
    listNode* temp;
    newNode = (listNode*)malloc(sizeof(listNode));
    strcpy(newNode -> data, x);
    newNode -> link = NULL;
    if(L -> head == NULL)
    {
        L -> head = newNode;
        return;
    }
    // 현재 리스트가 공백이 아닌 경우
    temp =  L -> head;
    while(temp -> link != NULL)
        temp = temp -> link;
    temp -> link = newNode;
}

// 리스트에서 노드 p를 삭제하는 연산
void deleteNode(linkedList_h* L, listNode* p)
{
    listNode* pre;
    if(L->head == NULL)
        return;
    if(L->head->link == NULL)
    {
        free(L->head);
        L->head = NULL;
        return;
    }
    else if(p == NULL)
        return;
    else
    {
        pre = L->head;
        while(pre->link != p)
        {
            pre = pre->link;
        }
        pre->link = p->link;
        free(p);
    }
}
// 리스트에서 x 를 검색하는 연산
listNode* searchNode(linkedList_h* L, char* x)
{
   listNode* temp;
   temp = L->head;
   while (temp != NULL) {
      if (strcmp(temp->data, x) == 0)return temp;
      else temp = temp->link;
   }
   return temp;
}
// 리스트의 노드 순서를 역순으로 바꾸는 연산
void reverse(linkedList_h* L) {
   listNode* p;
   listNode* q;
   int stack_size = 0;
   int i;
   p = L->head;
   q = NULL;
   while (p != NULL) {
      stack_size++;
      p = p->link;
   }
   listNode** nodeStack = (listNode**)malloc(stack_size * sizeof(listNode*));
   p = L->head;
   for (i = stack_size - 1; i >= 0; i--) {
      nodeStack[i] = p;
      p = p->link;
   }
   L->head = nodeStack[0];
   q = L->head;
   for (i = 1; i < stack_size; i++) {
      q->link = nodeStack[i];
      q = q->link;
   }
   q->link = NULL;
   free(nodeStack);
}

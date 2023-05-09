//  main.cpp
//  230412
//
//  Created by 이지수 on 2023/04/10.
//
#include <stdio.h>
#include <stdlib.h>
#include <tchar.h>

typedef struct _node {
    int data;
    struct _node* next;
} node;

node* head, * tail;

void init_list() {
    head = (node*)malloc(sizeof(node));
    tail = (node*)malloc(sizeof(node));
    head->next = tail;
    tail->next = tail;
}

node* ordered_insert(int k) {
    node* newNode = (node*)malloc(sizeof(node));
    newNode->data = k;
    newNode->next = NULL;

    if (head->next->data >= 100000) {
        head->next = newNode;
        tail->next = newNode;
    }
    else {
        node* temp = head->next;
        node* pre = NULL;
        while (temp != tail && k > temp->data) {
            pre = temp;
            temp = temp->next;
        }

        if (pre == NULL) {
            newNode->next = temp;
            head->next = newNode;
        }
        else {
            newNode->next = temp;
            pre->next = newNode;
        }
    }

    return newNode;
}

void print_list(node* t) {
    int count = 0;
    printf("{");
    while (t != tail) {
        printf("%d", t->data);
        t = t->next;
        count++;
        if (count >= 10)
            break;
        if (t != tail)
            printf(", ");
    }
    printf("}\n");
}

void delete_node(int k) {
    node* pre = head;
    node* temp = head->next;
    while (temp != tail) {
        if (temp->data == k) {
            pre->next = temp->next;
            free(temp);
            return;
        }
        pre = temp;
        temp = temp->next;
    }
}

void free_list() {
    node* temp = head->next;
    while (temp != tail) {
        node* del = temp;
        temp = temp->next;
        free(del);
    }
    free(head);
    free(tail);
}

int _tmain(int argc, _TCHAR* argv[]) {
    init_list();
    ordered_insert(10);
    ordered_insert(5);
    ordered_insert(8);
    ordered_insert(3);
    ordered_insert(1);
    ordered_insert(7);

    // 초기의 리스트 출력
    printf("Initial Linked list is ");
    print_list(head->next);

    delete_node(8);
    // 8이 삭제 된 후의 리스트 출력
    print_list(head->next);

    free_list();

    return 0;
}

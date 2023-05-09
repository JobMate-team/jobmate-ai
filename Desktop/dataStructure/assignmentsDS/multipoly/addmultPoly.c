#include <stdio.h>
#include "addmultPoly.h"

polynomial addPoly(polynomial A, polynomial B)
{
    polynomial C;
    int A_index = 0, B_index = 0, C_index = 0;
    int A_degree = A.degree, B_degree = B.degree;
    C.degree = MAX(A.degree, B.degree);
    
    while(A_index <= A.degree && B_index <= B.degree)
    {
        if(A_degree > B_degree)
        {
            C.coef[C_index++] = A.coef[A_index++];
            A_degree--;
        }
        else if(A_degree == B_degree)
        {
            C.coef[C_index++] = A.coef[A_index++] + B.coef[B_index++];
            A_degree--;
            B_degree--;
        }
        else
        {
            C.coef[C_index++] = B.coef[B_index++];
            B_degree--;
        }
    }
    return C;
}
polynomial multPoly(polynomial A, polynomial B)
{
    polynomial D;
    int A_index = 0, B_index = 0, D_index = 0;
    int A_degree = A.degree, B_degree = B.degree;
    D.degree = A.degree + B.degree;
    
    for(int i = 0; i < A.degree + B.degree + 1; i++)
    {
        D.coef[i] = 0;
    }
    for(A_index = 0; A_index < A.degree+1; A_index++)
    {
        for(B_index = 0; B_index < B.degree+1; B_index++)
        {
            D.coef[A_index + B_index] += A.coef[A_index] * B.coef[B_index];
        }
    }
    return D;
}

void printPoly(polynomial P)
{
    int i, degree;
    degree = P.degree;
    
    for(i = 0; i <= P.degree; i++)
    {
        printf("%3.0fx^%d", P.coef[i], degree--);
        if(i < P.degree)
            printf(" +");
    }
    printf("\n");
}

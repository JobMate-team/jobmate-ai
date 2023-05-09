#include <stdio.h>
#include "addmultPoly.h"

int main(void)
{
    polynomial A = {3, {4, 3, 5, 0}};
    polynomial B = {4, {3, 1, 0, 2, 1}};
    polynomial C;
    polynomial D;
    
    C = addPoly(A, B);
    D = multPoly(A,B);
    
    printf("\n A(x) = ");
    printPoly(A);
    printf("\n B(x) = ");
    printPoly(B);
    printf("\n C(x) = ");
    printPoly(C);
    printf("\n D(x) = ");
    printPoly(D);
    
    getchar();
    return 0;
}

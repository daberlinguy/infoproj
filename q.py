def quicksort(l):
    le=len(l)
    if le<=1:return l
    pivot=l[-1]
    left=[]
    right=[]

    for i in range(le):
        e=l[i]
        if i >= le-1:
            break
        elif e < pivot:
            left+=[e]
        elif e >= pivot:
            right+=[e]

    return quicksort(left)+[pivot]+quicksort(right)

print(quicksort([9,4,2,6,3,5,1,8,7]))

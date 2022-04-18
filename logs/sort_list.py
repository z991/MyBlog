def merge_sort(a, b):
    ret = []
    i = j = 0
    while len(a) >= i + 1 and len(b) >= j + 1:
        if a[i] <= b[j]:
            ret.append(a[i])
            i += 1
        else:
            ret.append(b[j])
            j += 1

    if len(a) > i:
        ret += a[i:]
    if len(b) > j:
        ret += b[j:]
    return ret


if __name__ == '__main__':
    a = [1, 3, 7, 11]
    b = [2, 4, 6, 8]
    print(merge_sort(a, b))

import numpy as np

ans = []
with open('../results/FINDER_ND/synthetic/result.txt') as f:
    list = f.readline()
    print(list)
    tmp = ''
    for i in range(len(list)):
        if list[i].isdigit():
            tmp += list[i]
        else:
            if tmp != '':
                ans.append(tmp)
                tmp = ''
print(ans)
class A:
    def __init__(self, num):
        self.num = num


l = [A(i) for i in range(10)]

for p in l:
    print(p.num, end=' ')
    p.num += 1
print()
k = l[:3]
for p in k:
    print(p.num, end=' ')

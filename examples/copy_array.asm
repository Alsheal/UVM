; Копирование массива: mem[100..104] -> mem[200..204]

; Исходный массив
ldc r0, 100
ldc r1, 11
st  r0, r1
ldc r0, 101
ldc r1, 22
st  r0, r1
ldc r0, 102
ldc r1, 33
st  r0, r1
ldc r0, 103
ldc r1, 44
st  r0, r1
ldc r0, 104
ldc r1, 55
st  r0, r1

; Копирование
ld  r2, 100
ldc r3, 200
st  r3, r2
ld  r2, 101
ldc r3, 201
st  r3, r2
ld  r2, 102
ldc r3, 202
st  r3, r2
ld  r2, 103
ldc r3, 203
st  r3, r2
ld  r2, 104
ldc r3, 204
st  r3, r2
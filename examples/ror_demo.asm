; Демонстрация ror: результаты сохраняются в mem[20] и mem[21]

; Величины сдвига: mem[10] = 4, mem[11] = 1
ldc r0, 10
ldc r1, 4
st  r0, r1
ldc r0, 11
ldc r1, 1
st  r0, r1

; 0x12345678 ror 4 = 0x81234567
ldc r2, 305419896
ror r2, 10
ldc r3, 20
st  r3, r2

; 1 ror 1 = 0x80000000
ldc r4, 1
ror r4, 11
ldc r5, 21
st  r5, r4
import sys
import numpy
print(1111111111111)
numbers = sys.argv[1].split(',')
shape = tuple(int(num) for num in numbers)
print(shape)
print(sys.argv[2])
print(sys.argv[3])
print(2222222222222)
numbers = sys.argv[1].strip('()').split(',')
# 문자열에서 추출한 숫자를 정수로 변환하고 튜플로 만들기
result_tuple = tuple(int(num) for num in numbers)

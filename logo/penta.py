import math

sides = 5
len = 0.383

for i in range(sides):
    a = (i * 2 * math.pi/sides) - (math.pi)
    x = len * math.sin(a)
    y = len * math.cos(a)
    print(i, (x+1)*500, (y-1)*-500)

    
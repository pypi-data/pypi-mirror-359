from framer import Framer
import msvcrt
import time

x = Framer()
x.initwin(color="a", fps=1000)
k = 1
key = []
start = time.time()
while k <= (x.pixels + x.cols ):
    a = (k % x.cols)
    if a == 0:
        a = x.cols
    else:
        a = a
    b = (k // x.cols)
    # if b == 35:
        #print("yes")
    x.addObj(a, b, "*")
    n = x.renderFrame()
    if n != None:
        key.append(n)
    k += 1
end = time.time()
print(x.pixels)
print(end - start)
print( x.pixels / (end - start) )
print(key)
print(len(key))
# x.renderFrame()
# print(x.cols)
# print(x.lines)
# print(x.frame)
msvcrt.getch()
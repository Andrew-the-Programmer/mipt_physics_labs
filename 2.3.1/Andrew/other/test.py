from my_physics import *

def f(x, y):
    return x**2 + x * y**2

a, b = sp.symbols('x y')

def fprime(x, y):
    return sp.diff(f(x,y), x)

print(fprime(a, b)) #This works.

print(fprime(1, 1)) 

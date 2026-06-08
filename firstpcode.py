g = 10

def mystery_function1(x):
    global g
    l = 50
    g += 20
    l += 5
    return x + l + g

def mystery_function2(x):
    g=x
    return g

#result = mystery_function1(3)
mystery_function2(3)
result = g
print(result)
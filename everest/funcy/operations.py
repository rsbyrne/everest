################################################################################

def getitem(x, y):
    return x[y]

def call(x, y):
    return x(y)
def amp(x, y):
    return x and y
def bar(x, y):
    return x or y
def hat(x, y):
    return (x or y) and not (x and y)
# def exc(x, e, y):
#     t
def inv(val):
    return not val

################################################################################

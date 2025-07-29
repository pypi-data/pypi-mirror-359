# this file should be an example how to create two vectors with PyTNL and add them together (+)

import tnl

# ...
size = 10
a = tnl.Vector(size)
b = tnl.Vector(size)

# ...
for i in range(size):
    a[i] = 0
    b[i] = i + 42

# ...
print(list(a))
print(list(b))

# ...
# c = a + b
c = tnl.Vector()
# c.assign(a + b)  # same problem!
c.assign(a)
c += b
print(list(c))

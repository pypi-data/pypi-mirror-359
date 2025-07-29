# this file should be an example how to create a vector

import tnl

# ...
size = 10
a = tnl.Vector(size)

# ...
for i in range(size):
    a[i] = i + 42

# ...
print(list(a))

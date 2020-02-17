#!python3

import bmc

# standard

bm = bmc.BMC(0, False, False)

a = 'ABC'
c = bm.encodeA2BM(a)
#print(c)
assert(c == b'\x1f\x03\x19\x0e')
aa = bm.decodeBM2A(c)
#print(aa)
assert(a.upper() == aa)

a = 'Lorem Ipsum Dolor Sit Amet.'
bm.reset()
c = bm.encodeA2BM(a)
#print(c)
assert(c == b'\x1f\x12\x18\n\x01\x1c\x04\x06\x16\x05\x07\x1c\x04\t\x18\x12\x18\n\x04\x05\x06\x10\x04\x03\x1c\x01\x10\x1b\x1c')
aa = bm.decodeBM2A(c)
#print(aa)
assert(a.upper() == aa)

a = 'a1b2c3d4e5f6g7h8i9j0'
bm.reset()
c = bm.encodeA2BM(a)
#print(c)
assert(c == b'\x1f\x03\x1b\x17\x1f\x19\x1b\x13\x1f\x0e\x1b\x01\x1f\t\x1b\n\x1f\x01\x1b\x10\x1f\r\x1b\x15\x1f\x1a\x1b\x07\x1f\x14\x1b\x06\x1f\x06\x1b\x18\x1f\x0b\x1b\x16')
aa = bm.decodeBM2A(c)
#print(aa)
assert(a.upper() == aa)

# flipped bits

bm = bmc.BMC(0, True, False)

a = 'ABC'
c = bm.encodeA2BM(a)
#print(c)
assert(c == b'\x1f\x18\x13\x0e')
aa = bm.decodeBM2A(c)
#print(aa)
assert(a == aa)

print(__name__, 'OK')
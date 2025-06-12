
# fixedStrings are serialized with 2 bytes, assuming the fixedString
# is less than 65535. if the two deserialized bytes are 65535
# (0xffff), then that is a signal to deserialize in a way that is
# TBD. it is an error to deserialize a fixedString of zero.  for best
# forward compatibility, applications should get in the habit of using
# the data returned from the `deserialize` call instead of relying on
# 2-byte usage.

MULITBYTE_DESERIALIZE_MARKER = 0xffff

def serialize(fs, barray = None):
    assert(fs > 0 and fs < MULITBYTE_DESERIALIZE_MARKER)
    fsdata = bytearray() if None == barray else barray
    fsdata.append((fs >> 8) & 0xff)
    fsdata.append(fs & 0xff)
    if None == barray:
        return bytes(fsdata)
    else:
        return barray

def serializationSize(fs):
    assert(fs > 0 and fs < MULITBYTE_DESERIALIZE_MARKER)
    return 2

def deserialize(data):
    assert(len(data) >= 2)
    fs = (int(data[0]) << 8) + int(data[1])
    assert(fs > 0 and fs < MULITBYTE_DESERIALIZE_MARKER)
    return fs, data[2:]

def toString(arg):
    from . import fs
    return fs.toString(int(arg))

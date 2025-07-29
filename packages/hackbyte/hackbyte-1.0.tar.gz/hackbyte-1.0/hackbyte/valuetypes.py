import struct

def parse_value(type_, value):
    if type_ == 'dword':
        return struct.pack('<i', int(value))
    elif type_ == 'qword':
        return struct.pack('<q', int(value))
    elif type_ == 'float':
        return struct.pack('<f', float(value))
    elif type_ == 'double':
        return struct.pack('<d', float(value))
    elif type_ == 'byte':
        return bytes([int(value)])
    elif type_ == 'string':
        return value.encode()
    else:
        raise ValueError("Unsupported type")



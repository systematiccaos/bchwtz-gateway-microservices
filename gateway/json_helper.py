from binascii import hexlify

def bytes_to_strings(d: bytes):
    if isinstance(d, bytes) or isinstance(d, bytearray):
        return hexlify(d).decode('utf-8')  # Decode bytes to string
    elif isinstance(d, dict):
        return {k: bytes_to_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [bytes_to_strings(item) for item in d]
    else:
        return d
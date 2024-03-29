from binascii import hexlify

def bytes_to_strings(d):
    if isinstance(d, bytes):
        return hexlify(d).decode('ascii')  # Decode bytes to string
    elif isinstance(d, dict):
        return {k: bytes_to_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [bytes_to_strings(item) for item in d]
    else:
        return d
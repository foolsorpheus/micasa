# Cyphertext
def encrypt(content: str):
    if content is not None and len(content) > 0:
        data = bytearray(content.encode("UTF-8"))
        i = -85
        for i2 in range(len(data)):
            original_byte = data[i2]
            data[i2] = (i ^ original_byte) & 0xFF
            i = original_byte
        return data

def decrypt(data: bytearray):
    if data is not None and len(data) > 0:
        res = bytearray(data)
        i = -85
        for i2 in range(len(res)):
            decrypted_byte = (i ^ res[i2]) & 0xFF
            res[i2] = decrypted_byte
            i = decrypted_byte
        return res.decode("UTF-8")
    
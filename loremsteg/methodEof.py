
import zlib
import os
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

magic = b"tT1s-i5+Th3_3Nd"
def putEoF(inFilePath : str, outFilePath : str, data : bytes):
    o_file = open(outFilePath, "wb")
    if inFilePath != outFilePath:
        i_file = open(inFilePath, "rb")
        o_file.write(i_file.read())
        i_file.close()
    
    o_file.seek(0,os.SEEK_END)
    o_file.write(data)
    o_file.write(len(data).to_bytes(4))
    o_file.write(magic)
    o_file.close()

def takeEoF(inFilePath : str, remove : bool) -> bytes:
    i_file = open(inFilePath, "r+b")
    i_file.seek(-len(magic)-4, os.SEEK_END)
    data_s = int.from_bytes(i_file.read(4))
    if i_file.read() != magic:
        raise TypeError("Wrong file magic!")
    i_file.seek(-len(magic)-4-data_s, os.SEEK_END)
    trunc = i_file.tell()
    data = i_file.read(data_s)
    if remove:
        i_file.truncate(trunc)
    return data

def hideEoF(inFilePath : str, outFilePath : str, data : bytes, key : bytes):
    with open(outFilePath, "wb") as o_file:
        if inFilePath != outFilePath:
            i_file = open(inFilePath, "rb")
            o_file.write(i_file.read())
            i_file.close()

        nonce = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        data = zlib.compress(data)
        data = cipher.encrypt(data)

        o_file.seek(0,os.SEEK_END)
        o_file.write(len(data).to_bytes(7,'little'))
        o_file.write(data)
        o_file.write(len(data).to_bytes(7,'little'))
        o_file.write(nonce)

def revealEoF(inFilePath : str, key : bytes) -> bytes | None:
    data = None
    with open(inFilePath, "rb") as i_file:
        i_file.seek(-23, os.SEEK_END)
        size = int.from_bytes(i_file.read(7),'little')
        nonce = i_file.read(16)

        decipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        i_file.seek(-30-size, os.SEEK_END)
        if size != int.from_bytes(i_file.read(7),'little'):
            return None
        data = i_file.read(size)
        data = decipher.decrypt(data)
        data = zlib.decompress(data)
    return data

def removeEoF(inFilePath : str):
    with open(inFilePath, "r+b") as i_file:
        i_file.seek(-23, os.SEEK_END)
        size = int.from_bytes(i_file.read(7),'little')

        i_file.seek(-30-size, os.SEEK_END)
        if size != int.from_bytes(i_file.read(7),'little'):
            return
        i_file.seek(-30-size, os.SEEK_END)
        i_file.truncate(i_file.tell())

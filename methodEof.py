magic = b"Eof "

import os

def encodeEoF(inFilePath : str, outFilePath : str, data : bytes):
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

def decodeEoF(inFilePath : str) -> bytes:
    i_file = open(inFilePath, "rb")
    i_file.seek(-len(magic), os.SEEK_END)
    if i_file.read() != magic:
        raise TypeError("Wrong file magic!")
    i_file.seek(-len(magic)-4, os.SEEK_END)
    data_s = int.from_bytes(i_file.read(4))
    i_file.seek(-len(magic)-4-data_s, os.SEEK_END)
    return i_file.read(data_s)

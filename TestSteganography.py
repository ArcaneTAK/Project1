from methodEoF import encodeEoF, decodeEoF
from methodAudio import tryEncodeAudio
import rsa

def testMethodEoF():
    data = b"Hello World"
    inFilePath = r"TestFile\#1 bedwars trap.mp4"
    outFilePath = r"Result\#1 bedwars trap.mp4"
    encodeEoF(inFilePath, outFilePath, data)
    fileData = decodeEoF(outFilePath)
    if fileData != data:
        raise ValueError("Unsuccessful")

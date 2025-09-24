from typing import *
import moviepy
import numpy
import os
import struct

magic = b"Audio   "
supportedAudio = set([".mp3",".wav",".aac",".webm",".flac",".mp1",".mp2"])

def replace8lsb(i, data):
    a = bytearray(numpy.float32(i).tobytes())
    a[0] = data
    return numpy.frombuffer(a, numpy.float32)
def tryEncodeAudio(inFilePath : str, outFilePath : str, data : bytes) -> bool:
    try:
        movie = None
        if os.path.splitext(inFilePath)[1] in supportedAudio:
            aud = moviepy.AudioFileClip(inFilePath)
        else:
            movie = moviepy.VideoFileClip(inFilePath)
            aud = movie.audio
            if aud == None:
                aud = moviepy.AudioClip(None,movie.duration,movie.fps)
    except:
        return False
    if ((aud.duration-1) * aud.fps) * 2 < len(data) - 8:
        return False

    data_s = len(data).to_bytes(8)
    iter = aud.iter_frames()
    i = aud.get_frame(0.5)
    i[0] = numpy.float64(0.0001) # replace8lsb(i[0], data_s[j])
    i[1] = numpy.float64(0.0001) # replace8lsb(i[1], magic[j])
    print(i.tobytes())

    # index = 0
    # while index < len(data) and (i := next(iter)) is not None:
    #     i[0] = replace8lsb(i[0], data[index])
    #     index += 1
    #     if index < len(data):
    #         i[1] = replace8lsb(i[1], data[index])
    #     index += 1

    if movie:
        if os.path.splitext(outFilePath)[1] in supportedAudio:
            aud.write_audiofile(outFilePath, codec = 'ale')
        else:
            movie.write_videofile(outFilePath)
        movie.close()
    else:
        aud.write_audiofile(outFilePath)
        aud.close()
    return True

def get8lsb(i):
    return numpy.float32(i).tobytes()[0]

def decodeAudio(inFilePath : str) -> bytes:
    movie = None
    if os.path.splitext(inFilePath)[1] in supportedAudio:
        aud = moviepy.AudioFileClip(inFilePath)
    else:
        movie = moviepy.VideoFileClip(inFilePath)
        aud = movie.audio
        if aud == None:
            aud = moviepy.AudioClip(None,movie.duration,movie.fps)
    
    data_s = bytearray(8)
    this_magic = bytearray(8)
    iter = aud.iter_frames()
    if this_magic != magic:
        print(data_s, this_magic)
        raise TypeError("Wrong file magic!")
    index = 0
    data = bytearray(data_s)
    while index < len(data) and (i := next(iter)) is not None:
        data[index] = get8lsb(i[0])
        index += 1
        if index < len(data):
            data[index] = get8lsb(i[1])
        index += 1

    if movie:
        movie.close()
    else:
        aud.close()
    return data
tryEncodeAudio(r"Result\#3 bedwars trap.wav", r"Result\#3 bedwars trap.wav", b"Hello World")
print(decodeAudio(r"Result\#3 bedwars trap.wav"))
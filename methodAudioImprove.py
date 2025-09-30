from typing import *
import moviepy
import numpy as np
from moviepy import AudioClip

def tryEncodeAudio(inCover : AudioClip, inSecret : AudioClip):
    def new_frame(t):
        cov = inCover.get_frame(t)
        if len(cov.shape) != 1:
            cov = cov[:,0]
        try:
            sec = inSecret.get_frame(t)
            if len(sec.shape) != 1:
                sec = sec[:,0]
            diff = len(cov) - len(sec)
            sec = np.pad(sec, (0,diff), "constant", constant_values=0)
        except:
            sec = np.zeros(len(cov))
        sec = np.frombuffer(sec.tobytes(), dtype=np.uint64) & 0xffff000000000000 # take 16msb
        cov = np.frombuffer(cov.tobytes(), dtype=np.uint64) & 0xffff000000000000 # take 16msb
        new = cov | (sec >> 16)
        res = np.frombuffer(new.tobytes(), dtype=np.float64)
        return np.column_stack([res,res])
    return AudioClip(new_frame, inCover.duration, inCover.fps)

def decodeAudio(inSecret : AudioClip):
    def new_frame(t):
        sec = np.array(inSecret.get_frame(t), dtype=np.float64).tobytes()
        sec = (np.frombuffer(sec, dtype=np.uint64) & 0x0000ffff00000000) << 16
        return np.frombuffer(sec.tobytes(), dtype=np.float64)
        
    return AudioClip(new_frame, inSecret.duration, inSecret.fps)
    
cover = moviepy.AudioFileClip(r"TestFile\music.mp3")
secret = moviepy.AudioFileClip(r"TestFile\#1 bedwars trap.mp4")
# the resulting audio is different from what is expected
tryEncodeAudio(cover, secret).write_audiofile(r"Result\Hello.mp4", nbytes = 4, codec = "flac")
enc = moviepy.AudioFileClip(r"Result\Hello.mp4", nbytes=4)
decodeAudio(enc).write_audiofile(r"Result\decode.mp4", nbytes = 4, codec = "flac")
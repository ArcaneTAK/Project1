from typing import *
import moviepy
import numpy as np
import os
from moviepy import AudioClip

magic = b"Audio   "
supportedAudio = set([".mp3",".wav",".aac",".webm",".flac",".mp1",".mp2"])

def tryEncodeAudio(inCover : AudioClip, inSecret : AudioClip):
    def new_frame(t):
        cov = np.array(inCover.get_frame(t), dtype=np.float32)
        try:
            sec = np.array(inSecret.get_frame(t), dtype=np.float32)
            diff = len(cov) - len(sec)
            sec = np.pad(sec, (0,diff),"constant",constant_values=0)
        except:
            sec = np.zeros(len(cov))
        sec = np.frombuffer(sec.tobytes(), dtype=np.uint32) & 0xff000000 # take 16msb
        cov = np.frombuffer(cov.tobytes(), dtype=np.uint32) & 0xff000000 # take 16msb
        new = cov | (sec >> 8)
        return np.frombuffer(new.tobytes(), dtype=np.float32)
    return AudioClip(new_frame, inCover.duration, inCover.fps)

def decodeAudio(inSecret : AudioClip):
    def new_frame(t):
        sec = np.array(inSecret.get_frame(t), dtype=np.float32).tobytes()
        sec = (np.frombuffer(sec, dtype=np.uint32) & 0x00ff0000) << 8
        return np.frombuffer(sec.tobytes(), dtype=np.float32)
        
    return AudioClip(new_frame, inSecret.duration, inSecret.fps)
    
cover = moviepy.AudioFileClip(r"TestFile\music.mp3")
secret = moviepy.AudioFileClip(r"TestFile\#1 bedwars trap.mp4")
tryEncodeAudio(cover, secret).write_audiofile(r"Result\Hello.mp3", nbytes = 4, bitrate = "3000K")
enc = moviepy.AudioFileClip(r"Result\Hello.mp3")
decodeAudio(enc).write_audiofile(r"Result\decode.mp3")
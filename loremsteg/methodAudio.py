import numpy as np
from moviepy import AudioClip
import moviepy as mp
def stackAudio(coverAudio : AudioClip, secretAudio : AudioClip):
    """StackAudio

    The written audio have to be lossless. If cover Audio is shorter than secret, than secret will be cut.
    """
    secretAudio = secretAudio.with_duration(duration = coverAudio.duration)
    def new_frame(t):
        covFrame = coverAudio.get_frame(t)
        if len(covFrame.shape) != 1:
            covFrame = covFrame[:,0]
        try:
            sec = secretAudio.get_frame(t)
            if len(sec.shape) != 1:
                sec = sec[:,0]
            diff = len(covFrame) - len(sec)
            sec = np.pad(sec, (0,diff), "constant", constant_values=0)
        except:
            sec = np.zeros(len(covFrame))
        sec = np.frombuffer(sec.tobytes(), dtype=np.uint64) & 0xffff000000000000 # take 16msb
        covFrame = np.frombuffer(covFrame.tobytes(), dtype=np.uint64) & 0xffff000000000000 # take 16msb
        new = covFrame | (sec >> 16)
        res = np.frombuffer(new.tobytes(), dtype=np.float64)
        return np.column_stack([res,res])
    return AudioClip(new_frame, coverAudio.duration, coverAudio.fps)

def unstackAudio(inSecret : AudioClip):
    def new_frame(t):
        sec = np.array(inSecret.get_frame(t), dtype=np.float64).tobytes()
        sec = (np.frombuffer(sec, dtype=np.uint64) & 0x0000ffff00000000) << 16
        return np.frombuffer(sec.tobytes(), dtype=np.float64)
    return AudioClip(new_frame, inSecret.duration, inSecret.fps)

def fileAudioStack(inCovVid : str, inSec : str, outfile : str):
    secret = mp.AudioFileClip(inSec)
    cover = mp.VideoFileClip(inCovVid)
    if cover.audio == None:
        raise ValueError("Video must have sound")
    new : mp.VideoClip = cover.with_audio(stackAudio(cover.audio, secret))
    new.write_videofile(filename = outfile,audio_codec = "flac", audio_nbytes = 4)
    
def fileAudioUnstack(inVid : str, outfile : str):
    enc = mp.AudioFileClip(inVid, nbytes=4)
    unstackAudio(enc).write_audiofile(outfile, nbytes = 4)
    enc.close()
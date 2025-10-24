import moviepy
import numpy as np
from moviepy import AudioClip

def hideInAudio(coverAudio: AudioClip, data: bytes):
    global d
    d =b"Magic" + len(data).to_bytes(7) + data + (b" " if len(data) % 2 else b"")
    global cur
    cur = 0
    def new_frame(t):
        global cur
        global d
        covFrame : np.ndarray = coverAudio.get_frame(t)
        if len(covFrame.shape) != 1:
            covFrame = covFrame[:,0]
        
        size = len(covFrame)
        sec = np.array(np.frombuffer(d[cur*2 : cur*2 + size*2], np.uint16), np.uint64) << 32
        cur += size
        diff = len(covFrame) - len(sec)
        sec = np.pad(sec, (0,diff), "constant", constant_values=0)
        

        covFrame = np.frombuffer(covFrame.tobytes(),np.uint64) & 0xffff000000000000
        res = covFrame | sec
        res = np.frombuffer(covFrame.tobytes(), dtype=np.float64)

        return np.column_stack([res,res])
    return AudioClip(new_frame, coverAudio.duration, coverAudio.fps)

def revealInAudio(coverAudio: AudioClip) -> bytes:
    d = bytearray()
    global c
    c = 1
    global k
    k = -1
    header = bytearray()
    def new_frame(t):
        covFrame : np.ndarray = coverAudio.get_frame(t)
        if len(covFrame.shape) != 1:
            covFrame = covFrame[:,0]
        sec = np.array(covFrame, dtype=np.float64)

        print(sec[:12].tobytes())

        sec = np.frombuffer(sec.tobytes(), dtype=np.uint64)
        print(sec[:12])
        sec = (sec & 0x0000ffff00000000) >> 32
        sec = np.array(sec,np.int16).tobytes()

        global c
        if c < 0:
            raise ValueError()
        c -= 1

        global k
        # if len(header) < 12:
        #     header.extend(sec[:12 - len(header)])
        #     if len(header) >= 12:
        #         k = int.from_bytes(header[5:12])
        # d.extend(sec)
        # if k > 0 and len(d) >= k:
        #     return
        return coverAudio.get_frame(t)
    AudioClip(new_frame, coverAudio.duration, coverAudio.fps).write_audiofile(r"Result\Chao.mp4", nbytes = 4, codec = "flac")
    return d

# cover = moviepy.AudioFileClip(r"TestFile\music.mp3")
# hideInAudio(cover, b"Hello World").write_audiofile(r"Result\Hello.mp4", nbytes = 4, codec = "flac")
enc = moviepy.AudioFileClip(r"Result\Hello.mp4", nbytes=4)
data = revealInAudio(enc)
print(data)
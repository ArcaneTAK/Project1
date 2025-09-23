import moviepy
import numpy
import os

magic = b"Audio   "
supportedAudio = set([".mp3",".wav",".aac",".webm",".flac",".mp1",".mp2"])

def replace8lsb(i, data):
    return ((i.astype(numpy.int64) >> 8) << 8) | data
def tryEncodeAudio(inFilePath : str, outFilePath : str, data : bytes) -> bool:
    try:
        if os.path.split(inFilePath)[1] in supportedAudio:
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
    
    # scuffed as fuck
    data_s = len(data).to_bytes(8)
    iter = aud.iter_frames()
    for i, j in zip(iter, range(8)):
        i[0] = replace8lsb(i[0], data_s[j])
        i[1] = replace8lsb(i[1], magic[j])
    index = 0
    while index < len(data) and (i := next(iter)) is not None:
        i[0] = replace8lsb(i[0], data[index])
        index += 1
        if index < len(data):
            i[1] = replace8lsb(i[1], data[j])
        index += 1

    if movie:
        if os.path.split(outFilePath) in supportedAudio:
            aud.write_audiofile(outFilePath)
            aud.close()
        else:
            movie.write_videofile(outFilePath)
        movie.close()
    else:
        aud.write_audiofile(outFilePath)
        aud.close()
    return True
print(
tryEncodeAudio(r"Result\#2 bedwars trap.mp4", r"Result\#3 bedwars trap.mp3",b"Hello World")
)
from loremsteg.methodEof import *
from loremsteg.methodAudio import *
from loremsteg.methodVidStructure import *

if __name__ == '__main__':
    while 1:
        mode = input('''
        |||WELCOME TO LOREM IPSUM STEGANOGRAPHY APP|||
        What do you want to do?
            0. Exit
            1. Inspect boxes
            2. Hida data in video structure
            3. Reveal data in video structure
            4. Encode data into audio
            5. Decode data from audio
            6. Hide data to EoF
            7. Reveal data from EoF
        ''')
        try:
            match mode:
                case '0':
                    break
                case '1':
                    cover = input('Select your video to inspect: ')
                    inspect(cover)
                case '2':
                    cov = input('Select your cover video: ')
                    sec = input('Select your secret data: ')
                    out = input('Select the path to output your file and the file name with specified header: ')
                    hide_free_box(cov, sec, out)
                    print(f"Success, output to: {out}")
                case '3':
                    cov = input('Select your cover video: ')
                    out = input('Select the path to output your file and the file name with specified header: ')
                    reveal_free_box(cov, out)
                    print(f"Success, output to: {out}")
                case '4':
                    cov = input('Select your cover video: ')
                    sec = input('Select your secret audio: ')
                    out = input('Select the path to output your file and the file name with specified header: ')
                    fileAudioStack(cov, sec, out)
                    print(f"Success, output to: {out}")
                case '5':
                    cov = input('Select your cover video: ')
                    out = input('Select the path to output your file and the file name with specified header: ')
                    fileAudioUnstack(cov, out)
                    print(f"Success, output to: {out}")
                case '6':
                    cov = input('Select your cover video: ')
                    sec = input('Select your secret data: ')
                    out = input('Select the path to output your file and the file name with specified header: ')
                    key = bytes.fromhex(input("Enter your key (hex encoded): "))
                    with open(sec, "rb") as f:
                        data = f.read()
                        hideEoF(cov, out, data, key)
                        print(f"Success, output to: {out}")
                case '7':
                    cov = input('Select your cover video: ')
                    key = bytes.fromhex(input("Enter your key (hex encoded): "))
                    out = input('Select the path to output your file and the file name with specified header: ')
                    data = revealEoF(cov, key)
                    if data == None:
                        print("Failed to reveal data, possibly wrong key")
                    else:
                        with open(out, "wb") as f:
                            f.write(data)
                        print(f"Success, output to: {out}")
                case _:
                    print('Error: Invalid syntax, try again.')
        except Exception as e:
            print(f'Error: {e}.')
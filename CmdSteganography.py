from methodEoF import hideEoF, revealEoF
from methodAudio import fileAudioStack, fileAudioUnstack
import sys
def main():
    method = input("Choose: 1. EoF with encryption; 2. Audio stacking")
    decide = input("Choose: 1. Hide; 2. Reveal")
    match method, decide:
        case "1","1":
            cov = input("Enter path to file to use as cover file")
            sec = input("Enter path to file to use as data")
            out = input("Enter path to file to output")
            key = bytes.fromhex(input("Enter key (hex encoded)"))
            with open(sec,"rb") as f:
                data = f.read()
                hideEoF(cov,out,data,key)
                print(f"Success, output to: {out}")
        case "1","2":
            cov = input("Enter path to file to use as cover file")
            out = input("Enter path to file to output")
            key = bytes.fromhex(input("Enter key (hex encoded)"))
            data = revealEoF(cov,key)
            if data == None:
                print("Failed to reveal data, possibly wrong key")
            else:
                with open(out,"wb") as f:
                    f.write(data)
                print(f"Success, output to: {out}")
        case "2","1":
            cov = input("Enter path to video file to use as cover file")
            sec = input("Enter path to audio file to use as secret data")
            out = input("Enter path to file to output")
            fileAudioStack(cov,sec,out)
            print(f"Success, output to: {out}")
        case "2","2":
            cov = input("Enter path to video file to use as cover file")
            out = input("Enter path to audio file to output")
            fileAudioUnstack(cov,out)
            print(f"Success, output to: {out}")
        case _, _:
            return


if __name__ == "__main__":
    main()
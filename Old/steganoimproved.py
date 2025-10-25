import os
import pickle
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def r_uint32(f):
    return int.from_bytes(f.read(4), 'big')


def r_type(f):
    return f.read(4).decode('ascii', errors='replace')


def split_str(main_str, substr_cnt):
    substr_len = int(len(main_str) / substr_cnt)
    
    substr_ls = []
    start = 0
    for _ in range(substr_cnt - 1):
        substr_ls.append(main_str[start:start + substr_len])
        start += substr_len
    substr_ls.append(main_str[start:])

    return substr_ls


def scramble(binary_data, scramble_ls, delimiter='\\xxx'):
    substr_ls = split_str(binary_data, len(scramble_ls))
    return b''.join((delimiter.encode() + substr_ls[i]) for i in scramble_ls)


def unscramble(binary_data, scramble_ls, delimiter='\\xxx'):
    substr_ls = binary_data.split(delimiter.encode())[1:]
    return b''.join(substr_ls[scramble_ls.index(i)] for i in range(len(scramble_ls)))


def hide_scramble_ls(binary_data, scramble_ls, position):
    scramble_binary = ''.join([f'\\x{num:0x}' for num in scramble_ls]).encode()
    return len(scramble_binary), binary_data[:position] + scramble_binary + binary_data[position:]


def get_scramble_ls(binary_data, position, size):
    scramble_ls = [int(x.decode(), 16) for x in binary_data[position:position + size].split(b'\\x')[1:]]
    return scramble_ls, binary_data[:position] + binary_data[position + size:]


def encrypt_file(data, scramble_ls=[], position=-1):
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(data, AES.block_size)
    encrypted = cipher.encrypt(padded)

    scramble_size = 0
    position = position if position >= 0 else random.randint(0, len(data) - 1)
    if len(scramble_ls) > 0:
        encrypted = scramble(encrypted, scramble_ls)
        scramble_size, encrypted = hide_scramble_ls(encrypted, scramble_ls, position)

    key_dict = {
        'key': key,
        'iv': iv,
        'scramble_pos': position,
        'scramble_size': scramble_size
    }
    with open('key.pkl', 'wb') as f:
        pickle.dump(key_dict, f)
    print('Key file saved: \'key.pkl\'. DO NOT LOSE THIS FILE!')

    print(len(encrypted))

    return encrypted


def decrypt_file(data, key_file):
    with open(key_file, 'rb') as f:
        key_dict = pickle.load(f)
    key, iv, scramble_pos, scramble_size = list(key_dict.values())

    print(len(data))

    if scramble_pos >= 0 and scramble_size > 0:
        scramble_ls, encrypted = get_scramble_ls(data, scramble_pos, scramble_size)
        encrypted = unscramble(encrypted, scramble_ls)
    else:
        encrypted = data

    cipher_dec = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher_dec.decrypt(encrypted)
    unpadded = unpad(decrypted, AES.block_size)

    return unpadded


def parse_boxes(path, types):
    f_size = os.path.getsize(path)
    boxes = []
    with open(path, 'rb') as f:
        while f.tell() < f_size:
            start = f.tell()
            b_size = r_uint32(f)
            b_type = r_type(f)

            h_size = 8
            if b_size == 1:
                b_size = int.from_bytes(f.read(8), 'big')
                h_size = 16
            p_size = b_size - h_size

            if b_type in types:
                boxes.append({
                    'box_start': start,
                    'box_type': b_type,
                    'payload_offset': start + h_size,
                    'payload_size': p_size
                })
            
            f.seek(start + b_size)

    return boxes


def inspect(path):
    f_size = os.path.getsize(path)
    with open(path, 'rb') as f:
        while f.tell() < f_size:
            start = f.tell()
            b_size = r_uint32(f)
            b_type = r_type(f)

            h_size = 8
            if b_size == 1:
                b_size = int.from_bytes(f.read(8), 'big')
                h_size = 16
            p_size = b_size - h_size
            
            print(f'{b_type} (size={b_size}, offset=0x{start:X}, header_size={h_size}, payload_size={p_size})')
            f.seek(start + b_size)


def hide_free_box(path, secret):
    with open('output.mp4', 'wb') as f:
        with open(path, 'rb+') as i:
            frees = parse_boxes(path, ['free'])
            for free in frees:
                i.seek(free['box_start'] + 4)
                i.write(b'moof')
            i.seek(0)
            f.write(i.read())

        with open(secret, 'rb') as s:
            data = s.read()

            print(f'Data length: {len(data)}')
            substr_cnt = int(input('How many segments do you want to split this data to, for scrambling? (Type 0 if you don\'t want to scramble): '))
            scramble_ls = list(range(substr_cnt))
            random.shuffle(scramble_ls)
            scramble_pos = int(input(f'Choose a position to hide your data (From 0 to {len(data) - 1}, type -1 if you want to randomize): '))
            data = encrypt_file(data, scramble_ls, scramble_pos)
        
            if len(data) + 8 > 0xFFFFFFFF:
                f.write((1).to_bytes(4, 'big'))
                f.write(b'free')
                f.write((len(data) + 16).to_bytes(8, 'big'))
            else:
                f.write((len(data) + 8).to_bytes(4, 'big'))
                f.write(b'free')

            f.write(data)


def reveal_free_box(path, save_file):
    data = b''
    frees = parse_boxes(path, ['free'])
    with open(path, 'rb') as f:
        for free in frees:
            f.seek(free['payload_offset'])
            data += f.read(free['payload_size'])

    if len(data) == 0:
        print('Nothing to find')
    else:
        with open(f'{save_file}', 'wb') as s:
            key_file = input('Enter yout key file (.pkl file): ')
            data = decrypt_file(data, key_file)

            s.write(data)


if __name__ == '__main__':
    while 1:
            mode = int(input('''
            |||WELCOME TO LOREM IPSUM STEGANOGRAPHY APP|||
            What do you want to do?
                0. Exit
                1. Inspect boxes
                2. Hida data in video
                3. Reveal data in video
            '''))
            if mode == 0:
                break
            else:
                try:
                    if mode == 1:
                        cover = input('Select your video to inspect: ')
                        inspect(cover)
                    elif mode == 2:
                        cover = input('Select your cover video: ')
                        secret = input('Select your secret data: ')
                        hide_free_box(cover, secret)
                        print('Finished hiding!')
                    elif mode == 3:
                        cover = input('Select your cover video: ')
                        secret = input('Type your secret file\'s name (including your file header, eg. \'.mp4\'): ')
                        reveal_free_box(cover, secret)
                        print('Finished revealing!')
                    else:
                        print('Error: Invalid syntax, try again.')
                except FileNotFoundError:
                    print('Error: File not found. Please try with another file.')
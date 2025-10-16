import os

def r_uint32(f):
    return int.from_bytes(f.read(4), 'big')


def r_type(f):
    return f.read(4).decode('ascii', errors='replace')


def parse_boxes(f, types, container, end_offset, indent=0):
    while f.tell() < end_offset:
        start = f.tell()
        size = r_uint32(f)
        box_type = r_type(f)

        h_size = 8
        if size == 1:
            size = int.from_bytes(f.read(8), 'big')
            h_size = 16
        p_size = size - h_size
        
        # print(' ' * indent + f'{box_type} (size={size}, offset=0x{start:X}, header_size={h_size}, payload_size={p_size})')

        if box_type in types:
            container.append({
                'box_type': box_type,
                'payload_offset': start + h_size,
                'payload_size': p_size
            })
        else:
            f.seek(start + size)


def hide_free_box(path, secret):
    with open(path, 'ab') as f:
        sec_size = os.path.getsize(secret)
        if sec_size + 8 > 0xFFFFFFFF:
            f.write((1).to_bytes(4, 'big'))
            f.write(b'free')
            f.write((sec_size + 16).to_bytes(8, 'big'))
        else:
            f.write((sec_size + 8).to_bytes(4, 'big'))
            f.write(b'free')

        with open(secret, 'rb') as s:
            f.write(s.read())


def reveal_free_box(path, savepath, filetype):
    b_str = b''
    frees = []
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        parse_boxes(f, ['free'], frees, size)
        for free in frees:
            f.seek(free['payload_offset'])
            b_str += f.read(free['payload_size'])

    if len(b_str) == 0:
        print('Nothing to find')
    else:
        with open(f'{savepath}.{filetype if filetype[0] != '.' else filetype[1:]}', 'wb') as s:
            s.write(b_str)

if __name__ == '__main__':
    while 1:
        mode = int(input('''
            What do you want to do?
                0. Exit
                1. Hida data in video
                2. Reveal data in video
        '''))
        if mode == 0:
            break
        elif mode == 1:
            cover = input('Select your cover video: ')
            secret = input('Select your secret data: ')
            hide_free_box(cover, secret)
        elif mode == 2:
            cover = input('Select your cover video: ')
            secret = input('Select your secret file\'s name: ')
            filetype = input('Select the data type: ')
            reveal_free_box(cover, secret, filetype)
        else:
            print('Invalid syntax, try again.')

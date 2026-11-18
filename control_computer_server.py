
import socket
import threading
import struct
import json
import time

import pyautogui
import cv2
import numpy as np
import mss

HOST = '0.0.0.0'
PORT = 1337

# PACKET FUNCTIONS

def send_packet(sock, packet_type, data):
    header = packet_type + struct.pack('!I', len(data))
    sock.sendall(header + data)


def receive_exact(sock, size):
    data = b''

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def receive_packet(sock):
    header = receive_exact(sock, 5)

    if header is None:
        return None, None

    packet_type = header[:1]
    size = struct.unpack('!I', header[1:])[0]

    data = receive_exact(sock, size)

    if data is None:
        return None, None

    return packet_type, data


# HANDLE CLIENT INPUT

KEY_MAP = {
    'return': 'enter',
    'esc': 'esc',
    'ctrl_l': 'ctrl',
    'ctrl_r': 'ctrl',
    'shift_l': 'shift',
    'shift_r': 'shift',
    'alt_l': 'alt',
    'alt_r': 'alt',
    'cmd': 'win',
    'cmd_l': 'win',
    'cmd_r': 'win',
    'page_up': 'pageup',
    'page_down': 'pagedown',
    'caps_lock': 'capslock'
}


def handle_input(data):
    event = json.loads(data.decode('utf-8'))

    action = event['type']

    if action == 'key':
        key = event['key']
        key = KEY_MAP.get(key, key)

        if len(key) == 1:
            pyautogui.write(key)
        else:
            pyautogui.press(key)

    elif action == 'move':
        screen_width, screen_height = pyautogui.size()

        x = int(event['x'] * screen_width)
        y = int(event['y'] * screen_height)

        pyautogui.moveTo(x, y)

    elif action == 'click':
        screen_width, screen_height = pyautogui.size()

        x = int(event['x'] * screen_width)
        y = int(event['y'] * screen_height)

        button = event['button']

        if event['pressed']:
            pyautogui.mouseDown(x, y, button=button)
        else:
            pyautogui.mouseUp(x, y, button=button)

    elif action == 'scroll':
        pyautogui.hscroll(event['dx'])
        pyautogui.scroll(event['dy'])


# RECEIVE INPUT

def input_thread(client_sock):
    while True:
        packet_type, data = receive_packet(client_sock)

        if packet_type is None:
            break

        if packet_type == b'I':
            handle_input(data)


# SEND SCREEN

def screen_thread(client_sock):
    with mss.mss() as sct:

        monitor = sct.monitors[1]

        while True:
            try:
                screenshot = np.array(sct.grab(monitor))

                frame = cv2.cvtColor(
                    screenshot,
                    cv2.COLOR_BGRA2BGR
                )

                success, encoded = cv2.imencode(
                    '.jpg',
                    frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 60]
                )

                if success:
                    send_packet(
                        client_sock,
                        b'S',
                        encoded.tobytes()
                    )

                time.sleep(0.1)

            except (ConnectionError, OSError):
                break


# MAIN

if __name__ == '__main__':

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f'Server listening on port {PORT}')

    client_socket, client_address = server_socket.accept()

    print(f'Client connected: {client_address}')

    client_socket.setsockopt(
        socket.IPPROTO_TCP,
        socket.TCP_NODELAY,
        1
    )

    thread = threading.Thread(
        target=screen_thread,
        args=(client_socket,),
        daemon=True
    )

    thread.start()

    try:
        input_thread(client_socket)

    finally:
        client_socket.close()
        server_socket.close()

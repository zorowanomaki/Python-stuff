
import socket
import threading
import struct
import json

import pyautogui
import cv2
import numpy as np

from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

HOST = '10.0.0.25'  # Replace with server's IP
PORT = 1337

pyautogui.PAUSE = 0

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client_socket.connect((HOST, PORT))

client_socket.setsockopt(
    socket.IPPROTO_TCP,
    socket.TCP_NODELAY,
    1
)

send_lock = threading.Lock()


# PACKET FUNCTIONS

def send_packet(packet_type, data):
    header = packet_type + struct.pack('!I', len(data))

    with send_lock:
        client_socket.sendall(header + data)


def receive_exact(size):
    data = b''

    while len(data) < size:
        chunk = client_socket.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def receive_packet():
    header = receive_exact(5)

    if header is None:
        return None, None

    packet_type = header[:1]
    size = struct.unpack('!I', header[1:])[0]

    data = receive_exact(size)

    return packet_type, data


# SEND KEYBOARD

def on_press(key):
    try:
        key_data = key.char
    except AttributeError:
        key_data = key.name

    if key_data:
        event = {
            'type': 'key',
            'key': key_data
        }

        send_packet(
            b'I',
            json.dumps(event).encode('utf-8')
        )


# SEND MOUSE

local_width, local_height = pyautogui.size()


def normalize_coordinates(x, y):
    return x / local_width, y / local_height


def on_move(x, y):
    nx, ny = normalize_coordinates(x, y)

    event = {
        'type': 'move',
        'x': nx,
        'y': ny
    }

    send_packet(
        b'I',
        json.dumps(event).encode('utf-8')
    )


def on_click(x, y, button, pressed):
    nx, ny = normalize_coordinates(x, y)

    event = {
        'type': 'click',
        'x': nx,
        'y': ny,
        'button': button.name,
        'pressed': pressed
    }

    send_packet(
        b'I',
        json.dumps(event).encode('utf-8')
    )


def on_scroll(x, y, dx, dy):
    event = {
        'type': 'scroll',
        'dx': dx,
        'dy': dy
    }

    send_packet(
        b'I',
        json.dumps(event).encode('utf-8')
    )


# START INPUT LISTENERS

keyboard_listener = KeyboardListener(
    on_press=on_press
)

mouse_listener = MouseListener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll
)

keyboard_listener.start()
mouse_listener.start()


# RECEIVE AND DISPLAY SCREEN

cv2.namedWindow(
    'Remote Screen',
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    'Remote Screen',
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

try:
    while True:

        packet_type, data = receive_packet()

        if packet_type is None:
            break

        if packet_type == b'S':

            image_array = np.frombuffer(
                data,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if frame is not None:
                cv2.imshow('Remote Screen', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

finally:
    keyboard_listener.stop()
    mouse_listener.stop()

    client_socket.close()
    cv2.destroyAllWindows()

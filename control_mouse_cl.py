#client code
import socket
import io
import threading
import pyautogui
import struct
import time
from pynput.keyboard import Controller, Key

LOOPBACK = '127.0.0.1'
HOST = LOOPBACK
PORT = 1337

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

keyboard = Controller()
KEY_MAP = {
    'enter': Key.enter,
    'space': Key.space,
    'backspace': Key.backspace,
    'tab': Key.tab,
    'shift': Key.shift,
    'shift_l': Key.shift_l,
    'shift_r': Key.shift_r,
    'ctrl': Key.ctrl,
    'ctrl_l': Key.ctrl_l,
    'ctrl_r': Key.ctrl_r,
    'alt': Key.alt,
    'alt_l': Key.alt_l,
    'alt_r': Key.alt_r,
    'esc': Key.esc,
    'up': Key.up,
    'down': Key.down,
    'left': Key.left,
    'right': Key.right,
    'delete': Key.delete,
    'home': Key.home,
    'end': Key.end,
    'page_up': Key.page_up,
    'page_down': Key.page_down,
    'caps_lock': Key.caps_lock
}
buffer = ''

pyautogui.PAUSE = 0

while True:
    data = client_socket.recv(4096)

    if not data:
        break

    buffer += data.decode('utf-8')

    messages = buffer.split('\n')
    buffer = messages.pop()

    # Keep only the latest mouse movement
    latest_move = None

    for message in messages:
        if not message:
            continue

        if message.startswith('KEY:'):
            key = message[4:]
            key = KEY_MAP.get(key, key)
            keyboard.press(key)
            keyboard.release(key)

        elif message.startswith('MOUSE:'):
            parts = message[6:].split(',')

            action = parts[0]

            if action == 'move':
                latest_move = (int(parts[1]), int(parts[2]))

            elif action == 'click':
                pyautogui.click(
                    int(parts[1]),
                    int(parts[2])
                )

            elif action == 'scroll':
                pyautogui.scroll(int(parts[3]))

    # Execute only the most recent movement
    if latest_move is not None:
        pyautogui.moveTo(*latest_move)


#while True:
#    data = client_socket.recv(1024)
#
#    if not data:
#        break
#
#    buffer += data.decode('utf-8')
#
#    while '\n' in buffer:
#        message, buffer = buffer.split('\n', 1)
#
#        if message.startswith('KEY:'):
#            key = message[4:]
#            keyboard.press(key)
#            keyboard.release(key)
#
#        elif message.startswith('MOUSE:'):
#            parts = message[6:].split(',')
#
#            if parts[0] == 'move':
#                pyautogui.moveTo(int(parts[1]), int(parts[2]))
#
#            elif parts[0] == 'click':
#                pyautogui.click(int(parts[1]), int(parts[2]))
#
#            elif parts[0] == 'scroll':
#                pyautogui.scroll(int(parts[3]))

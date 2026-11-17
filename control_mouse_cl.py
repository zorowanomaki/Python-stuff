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

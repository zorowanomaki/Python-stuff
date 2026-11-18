#client code
import socket
import io
import pyautogui
import struct
import time


HOST = '10.0.0.25'

PORT = 1337

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

while True:
    screenshot = pyautogui.screenshot()

    # Saving the screenshot in a way where it would delete later (and encode)
    frame_buffer = io.BytesIO()
    screenshot.save(frame_buffer, format="JPEG")
    frame_data = frame_buffer.getvalue()

    #send size of frame
    frame_size = len(frame_data)
    client_socket.sendall(struct.pack('>L', frame_size))

    #send the screenshot back
    client_socket.sendall(frame_data)

    time.sleep(0.1)
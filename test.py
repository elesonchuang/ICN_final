import os 
import socket
import time
HOST = "127.0.0.1"
PORT = 7000
server_addr = (HOST, PORT)
FRAME_SIZE = 4096
file = open("videoplayback.mp4", "rb")
buffer = file.read()
print(buffer[-3:])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



l = 0
w = 0
while l <= len(buffer):
    s.sendto(buffer[l:l+FRAME_SIZE], server_addr)
    l += FRAME_SIZE
    #print(w)
    w+=1
    time.sleep(0.0001)

s.sendto(b'done', server_addr)
print("server start at: %s:%s" % (HOST, PORT))
print("wait for connection...")
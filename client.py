import socket
from packet.rtsp_packet import RTSPPacket 
import sys
from packet.rtp_packet import RTPPacket
from threading import Thread
import time
class Client:
    def __init__(self, server_ip: str, server_port: int, rtp_port: int, filepath: str):
        self.server_ip = server_ip
        self.rtsp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp.settimeout(0.05)
        self.rtsp.settimeout(0.1)
        self.server_port = server_port
        self.rtsp_connected = False
        self.rtp_port = rtp_port
        self.option = ["SETUP", "TEARDOWN", "PLAY", "PAUSE"]
        self.rtsp_seqnum = 0
        self.session = 123456
        self.filepath = filepath
        self.tempfilepath = "temp."+ self.filepath.split('.')[1]
        self.tempfile = open(self.tempfilepath, 'wb')
        self.has_start = False
        self.is_play = False
        self._rtp_receive_thread = None
        self.count = 0
        self.seq = -1
    def rtsp_connect(self):
        if self.rtsp_connected:
            print("already connected")
            return
        try:
            self.rtsp.connect((self.server_ip, self.server_port))
            self.rtsp_connected = True
            print(f"connect to server: {self.server_ip}:{self.server_port}")
        except:
            raise Exception(
                f'fail to connect rtsp server: {self.server_ip}:{self.server_port}')
    def _start_rtp_receive_thread(self):
        self._rtp_receive_thread = Thread(target=self.rtp_connect)
        self._rtp_receive_thread.setDaemon(True)
        self._rtp_receive_thread.start()

    def rtp_connect(self):
        try:
            self.rtp.bind((self.server_ip, self.rtp_port))
            print(f"connect rtp:{(self.server_ip, self.rtp_port)}")
        except:
            raise Exception(
                f"fail to connect rtp server: {self.server_ip}:{self.rtp_port}")
        while True:
            if not self.is_play:
                time.sleep(0.1)  # diminish cpu hogging
                continue
            self.get_data()

    def send_rtsp_request(self, request):
        '''
        request: [SETUP, TEARDOWN, PLAY, PAUSE]
        '''
        if request not in self.option:
            print("invalid rtsp request")
            return
        request_to_send = RTSPPacket(
            request, self.filepath, self.rtsp_seqnum, self.rtp_port).request_formatter()
        print(f"sending: {request_to_send.encode()}")
        self.rtsp.send(request_to_send.encode())
        self.rtsp_seqnum += 1
        return self.get_response()

    def send_setup(self):
        self.send_rtsp_request("SETUP")
        self.has_start = True
        self._start_rtp_receive_thread()

    def send_play(self):
        self.send_rtsp_request("PLAY")
        self.is_play = True

    def send_pause(self):
        self.send_rtsp_request("PAUSE")
        self.is_play = False

    def send_teardown(self):
        self.send_rtsp_request("TEARDOWN")
        self.has_start = False

    def get_response(self):
        temp = None
        while True:
            try:
                temp = self.rtsp.recv(4096)
                break
            except socket.timeout:
                pass
        print(RTSPPacket.response_parser(temp))

        return temp
    def get_data(self):
        temp = None
        while True:
            try:
                temp = self.rtp.recv(9192)
                break
            except socket.timeout:
                pass
        if temp:    
            payload = RTPPacket.get_packet_from_bytes(temp).payload
            seq = RTPPacket.get_packet_from_bytes(temp).sequence_num
            if seq - self.seq  != 1:print(seq)
            self.seq = seq
            self.tempfile.write(payload)
            #print(len(payload))

            
if __name__ == "__main__":
    c = Client("127.0.0.1", 5540, 5541, "1.mp4")
    #print(c.tempfilepath)
    # c.rtsp_connect()
    # c.send_setup()

    
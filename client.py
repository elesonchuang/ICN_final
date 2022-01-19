import socket

from rtsp_packet import RTSPPacket 
class Client:
    def __init__(self, server_ip, server_port, rtp_port, filepath):
        self.server_ip = server_ip
        self.rtsp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp.settimeout(0.005)
        self.rtsp.settimeout(0.1)
        self.server_port = server_port
        self.rtsp_connected = False
        self.rtp_port = rtp_port
        self.option = ["SETUP", "TEARDOWN", "PLAY", "PAUSE"]
        self.rtsp_seqnum = 0
        self.session = 123456
        self.filepath = filepath
        self.has_start = False
    def rtsp_connect(self):
        if self.rtsp_connected: 
            print("already connected")
            return
        try:
            self.rtsp.connect((self.server_ip, self.server_port))
            print(f"connect to server: {self.server_ip}:{self.server_port}")
        except:
            raise Exception(f'fail to connect to server: {self.server_ip}:{self.server_port}')
    def rtp_connect(self):
        self.rtp.bind()

    def send_rtsp_request(self, request):
        '''
        request: [SETUP, TEARDOWN, PLAY, PAUSE]
        '''
        if request not in self.option:
            print("invalid rtsp request")
            return
        request_to_send = RTSPPacket(request, self.filepath, self.rtsp_seqnum).requst_formatter()
        print(f"sending: {request_to_send.encode()}")
        self.rtsp.send(request_to_send.encode())
        self.rtsp_seqnum += 1
        return self.get_response()

    def send_setup(self):
        self.send_rtsp_request("SETUP")
        self.has_start = True
    def send_play(self):
        self.send_rtsp_request("PLAY")
        self.has_play = True
    def send_pause(self):
        self.send_rtsp_request("PAUSE")
        self.has_play = False
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
        print(temp)
        return temp
    
if __name__ == "__main__":
     Client("127.0.0.1", 5540, 5541, "test.py")


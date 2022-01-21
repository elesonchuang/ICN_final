import socket
import cv2
from typing import Union
from threading import Thread
from time import sleep
from io import BytesIO

from packet.rtsp_packet import RTSPPacket
from packet.rtp_packet import RTPPacket


class Server:
    DEFAULT_CHUNK_SIZE = 4096
    FRAME_SIZE = 4096 - 12
    CV_FRAME_SIZE = 4096

    def __init__(self, Host, Port, method):
        self.port = Port
        self.host = Host
        self.connection: Union[None, socket.socket] = None
        self.rtp_socket: Union[None, socket.socket] = None
        self.client_address = None
        self.state = "INIT"
        self.source_file = None
        self.method = None
        self.cv = cv2.VideoCapture(2)

    def connect_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (self.host, self.port)
        print(address)
        s.bind(address)
        print(f"Listening on {address[0]}:{address[1]}...")
        s.listen(1)
        print("Waiting for connection...")
        self.connection, self.client_address = s.accept()
        print(
            f"Accepted connection from {self.client_address[0]}:{self.client_address[1]}")

    def setup(self):
        if self.state != "INIT":
            raise Exception('server is already setup')
        while True:
            rtsp_packet = self.rtsp_recv()
            # TODO
            if rtsp_packet.request_type == 'SETUP':
                self.state = "PAUSED"
                print('State set to PAUSED')
                self.client_address = (
                    self.client_address[0], int(rtsp_packet.rtp_port))
                print(f"client: {self.client_address}")
                self.setup_rtp(rtsp_packet.filepath)
                self.send_rtsp_response(rtsp_packet)
                break
            # TODO FINISH

    def rtsp_recv(self, size=DEFAULT_CHUNK_SIZE) -> bytes:
        recv = None
        while True:
            try:
                recv = self.connection.recv(size)
                break
            except socket.timeout:
                continue
        print(f"Received from client: {repr(recv)}")
        recv = RTSPPacket.request_parser(recv)
        return recv

    def setup_rtp(self, video_file_path: str):
        print(f"Opening up video stream for file {video_file_path}")
        self.source_file = open(video_file_path, "rb")
        ##self._video_stream = VideoStream(video_file_path)
        print('Setting up RTP socket...')
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.method == 'cv':
            self._rtp_send_thread = Thread(target=self.cvcv)
        else:
            self._rtp_send_thread = Thread(target=self.handle_video_send)
        self._rtp_send_thread.setDaemon(True)
        self._rtp_send_thread.start()

    def handle_video_send(self):
        print(
            f"Sending video to {self.client_address[0]}:{self.client_address[1]}")
        buffer = self.source_file.read()
        print(len(buffer))
        l = 0
        w = 0
        while True:
            if self.state == 'TEARDOWN' or self.state == 'FINISH':
                print(w)
                return
            if self.state != 'PLAYING':
                sleep(0.5)  # diminish cpu hogging
                continue
            # TODO
            payload = buffer[l:l+self.FRAME_SIZE]
            l += self.FRAME_SIZE
            # print(w)

            rtp_packet = RTPPacket(
                payload_type=26,
                sequence_num=w,
                time_stamp=123,
                payload=payload
            )
            sleep(0.1)
            if w % 100 == 0:
                print(f"Sending packet #{w} to packet #{w+99}")
            print('Packet header:')
            # rtp_packet.print_header()
            # sleep(0.000001)
            packet = rtp_packet.get_packet()
            self.send_rtp_packet(packet)
            if l > len(buffer):
                self.state = "FINISH"
            w += 1

            # TODO FINISH

    def send_rtp_packet(self, packet):
        try:
            # print(len(packet))
            self.rtp_socket.sendto(
                packet, self.client_address)
        except socket.error as e:
            print(f"failed to send rtp packet: {e}")
            return

    def handle_rtsp_requests(self):
        print("Waiting for RTSP requests...")
        # main thread will be running here most of the time
        while True:
            packet = self.rtsp_recv()
            # assuming state will only ever be PAUSED or PLAYING at this point
            if packet.request_type == "PLAY":
                if self.state == 'PLAYING':
                    print('Current state is already PLAYING.')
                    continue
                self.state = 'PLAYING'
                print('State set to PLAYING.')
            elif packet.request_type == "PAUSE":
                if self.state == 'PAUSED':
                    print('Current state is already PAUSED.')
                    continue
                self.state = 'PAUSED'
                print('State set to PAUSED.')
            elif packet.request_type == "TEARDOWN":
                print('Received TEARDOWN request, shutting down...')
                self.send_rtsp_response(packet)
                self.connection.close()
                self.rtp_socket.close()
                self.state = 'TEARDOWN'
                raise ConnectionError('teardown requested')
            else:
                pass
            self.send_rtsp_response(packet)

    def send_rtsp_response(self, packet):
        response = packet.response_formatter()
        self.connection.send(response.encode())

    def cvcv(self):
        while True:
            if self.state == 'TEARDOWN' or self.state == 'FINISH':
                return
            if self.state != 'PLAYING':
                sleep(0.5)  # diminish cpu hogging
                continue
            ret, frame = self.cv.read()
            frame = cv2.resize(frame, (480, 360))

            frame = cv2.resize(frame, (480, 360), interpolation=cv2.INTER_AREA)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            success, img_buffer = cv2.imencode('.jpg', frame, encode_param)
            io_buf = BytesIO(img_buffer)
            io_buf.seek(0)
            buffer = io_buf.read()
            w = 0
            l = 0
            while l <= len(buffer):
                payload = buffer[l:l+self.CV_FRAME_SIZE]
                rtp_packet = RTPPacket(
                    payload_type=26,
                    sequence_num=w,
                    time_stamp=123,
                    payload=payload
                )
                self.send_rtp_packet(rtp_packet)
                l += self.CV_FRAME_SIZE
                sleep(1/100)

            sleep(0.1)
            if w % 100 == 0:
                print(f"Sending packet #{w} to packet #{w+99}")
            print('Packet header:')
            w += 1

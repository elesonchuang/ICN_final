import socket
from typing import Union
from threading import Thread
from time import sleep

from packet.rtsp_packet import RTSPPacket
from packet.rtp_packet import RTPPacket


class Server:
    DEFAULT_CHUNK_SIZE = 4096

    class STATE:
        INIT = 0
        PAUSED = 1
        PLAYING = 2
        FINISHED = 3
        TEARDOWN = 4

    def __init__(self, Port, Host):
        self.port = Port
        self.host = Host
        self.connection: Union[None, socket.socket] = None
        self.rtp_socket: Union[None, socket.socket] = None
        self.client_address = None
        self.state = self.STATE.INIT
        self.vedio_file_path = None

    def connect_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = self.host, self.port
        s.bind(address)
        print(f"Listening on {address[0]}:{address[1]}...")
        s.listen(1)
        print("Waiting for connection...")
        self.connection, self.client_address = s.accept()
        print(
            f"Accepted connection from {self.client_address[0]}:{self.client_address[1]}")

    def setup(self):
        if self.state == self.STATE.INIT:
            raise Exception('server is already setup')
        while True:
            rtsp_packet = self.rtsp_recv()
            # TODO
            if rtsp_packet.request_type == 'SETUP':
                self.server_state = self.STATE.PAUSED
                print('State set to PAUSED')
                self.client_address = self.client_address[0], rtsp_packet.rtp_port
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
        ##self._video_stream = VideoStream(video_file_path)
        print('Setting up RTP socket...')
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rtp_send_thread = Thread(target=self.handle_video_send)
        self._rtp_send_thread.setDaemon(True)
        self._rtp_send_thread.start()

    def handle_video_send(self):
        print(
            f"Sending video to {self.client_address[0]}:{self.client_address[1]}")
        while True:
            if self.server_state == self.STATE.TEARDOWN:
                return
            if self.server_state != self.STATE.PLAYING:
                sleep(0.5)  # diminish cpu hogging
                continue
            # TODO
            if self._video_stream.current_frame_number >= VideoStream.VIDEO_LENGTH-1:  # frames are 0-indexed
                print('Reached end of file.')
                self.server_state = self.STATE.FINISHED
                return
            frame = self._video_stream.get_next_frame()
            frame_number = self._video_stream.current_frame_number
            rtp_packet = RTPPacket(
                payload_type=26,
                sequence_num=frame_number,
                timestamp=frame_number*self.FRAME_PERIOD,
                payload=frame
            )

            print(f"Sending packet #{frame_number}")
            print('Packet header:')
            rtp_packet.print_header()
            packet = rtp_packet.get_packet()
            self.send_rtp_packet(packet)
            sleep(self.FRAME_PERIOD/1000.)
            # TODO FINISH

    def send_rtp_packet(self, packet):
        while packet:
            try:
                self.rtp_socket.sendto(
                    packet[:self.DEFAULT_CHUNK_SIZE], self.client_address)
            except socket.error as e:
                print(f"failed to send rtp packet: {e}")
                return
            packet = packet[self.DEFAULT_CHUNK_SIZE:]

    def handle_rtsp_requests(self):
        print("Waiting for RTSP requests...")
        # main thread will be running here most of the time
        while True:
            packet = self.rtsp_recv()
            # assuming state will only ever be PAUSED or PLAYING at this point
            if packet.request_type == "PLAY":
                if self.server_state == self.STATE.PLAYING:
                    print('Current state is already PLAYING.')
                    continue
                self.server_state = self.STATE.PLAYING
                print('State set to PLAYING.')
            elif packet.request_type == "PAUSE":
                if self.server_state == self.STATE.PAUSED:
                    print('Current state is already PAUSED.')
                    continue
                self.server_state = self.STATE.PAUSED
                print('State set to PAUSED.')
            elif packet.request_type == "TEARDOWN":
                print('Received TEARDOWN request, shutting down...')
                self.send_rtsp_response(packet)
                self.connection.close()
                # TODO
                self._video_stream.close()
                self.rtp_socket.close()
                self.server_state = self.STATE.TEARDOWN
                # for simplicity's sake, caught on main_server
                raise ConnectionError('teardown requested')
            else:
                # will never happen, since exception is raised inside `parse_rtsp_request()`
                # raise InvalidRTSPRequest()
                pass
            self.send_rtsp_response(packet)

    def send_rtsp_response(self, packet):
        response = packet.response_formatter()
        self.connection.send(response.encode())

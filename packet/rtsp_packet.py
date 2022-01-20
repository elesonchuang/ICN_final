import re


class RTSPPacket:
    def __init__(self, request_type, filepath, sequence_number, rtp_port=None, session=123456):
        self.request_type = request_type
        self.filepath = filepath
        self.sequence_num = sequence_number
        self.rtp_port = rtp_port
        self.session = session

    def __str__(self):
        return (
            f"""{self.request_type} rtsp://{self.filepath} RTSP/1.0
                CSeq: {self.sequence_num}
                Transport: RTP/UDP;client_port={self.rtp_port}
                Session: {self.session}
            """
        )

    def request_formatter(self):
        if self.request_type == "SETUP":
            return f"{self.request_type} rtsp://{self.filepath} RTSP/1.0\nCSeq: {self.sequence_num}\nTransport: RTP/UDP;client_port={self.rtp_port}\n"

        else:
            return f"{self.request_type} rtsp://{self.filepath} RTSP/1.0\nCSeq: {self.sequence_num}\nSession: {self.session}\n"

    def response_formatter(self, session = 123456):
        return (
        f"RTSP/1.0 200 OK\nCSeq: {self.sequence_num}\nSession: {session}\n"
        )

    @classmethod
    def request_parser(self, request: bytes) -> dict:
        match = re.match(
            r"(?P<request_type>\w+) rtsp://(?P<video_file_path>\S+) (?P<rtsp_version>RTSP/\d+.\d+)\r?\n"
            r"CSeq: (?P<sequence_number>\d+)\r?\n"
            r"(Range: (?P<play_range>\w+=\d+-\d+\r?\n))?"
            # in case of SETUP request
            r"(Transport: .*client_port=(?P<dst_port>\d+).*\r?\n)?"
            r"(Session: (?P<session_id>\d+)\r?\n)?",
            request.decode()
        )
        if not match:
            print("fail to parse request...")
            return
        dic = match.groupdict()
        return self(dic["request_type"], dic["video_file_path"], dic["sequence_number"], dic["dst_port"])

    @classmethod
    def response_parser(self, response: bytes) -> dict:
        match = re.match(
            r"(?P<rtsp_version>RTSP/\d+.\d+) 200 OK\r?\n"
            r"CSeq: (?P<sequence_number>\d+)\r?\n"
            r"Session: (?P<session_id>\d+)\r?\n",
            response.decode()
        )
        if not match:
            print("fail to parse response...")
            return
        dic = match.groupdict()
        return self(dic["request_type"], dic["video_file_path"], dic["sequence_number"], dic["dst_port"])


if __name__ == "__main__":
    test_text = RTSPPacket("SETUP", "test.py", 0, 2000).response_formatter(1)
    print(test_text)
    match = re.match(
        r"(?P<rtsp_version>RTSP/\d+.\d+) 200 OK\r?\n"
        r"CSeq: (?P<sequence_number>\d+)\r?\n"
        r"Session: (?P<session_id>\d+)\r?\n",
        test_text
    )
    # print(match.groupdict())
    r = RTSPPacket("SETUP", "test.py", 0, 2000).request_formatter().encode()
    print(RTSPPacket.request_parser(r))

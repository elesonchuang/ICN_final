class InvalidRTPPacket(Exception):
    pass

class RTPPacket : 
    HEADER_SIZE = 12 # 12 bytes

    VER = 0b10                 # 2 bit
    P = 0b0                     # 1 bit
    X = 0b0                     # 1 bit
    COUNTRIBUTOR_COUNT = 0x0    # 4 bit
    SSRC = 0x00000000           # 32 bit

    class PayloadType :
        JPEG = 26
    def __init__(
            self,
            M = 0b0,                    # 1 bit     1 for the end of data
            payload_type: int = 26,     # 7 bit
            sequence_num: int = None,   # 16 bit
            time_stamp: int = None,     # 32 bit
            payload: bytes = None) : 

        self.M = M
        self.payload_type = payload_type
        self.sequence_num = sequence_num
        self.time_stamp = time_stamp
        self.payload = payload

        b0 = (self.VER << 6) | (self.P << 5) | self.COUNTRIBUTOR_COUNT
        b1 = self.M << 7 | self.payload_type
        b2 = self.sequence_num >> 8
        b3 = self.sequence_num & 0xFF
        b4_7 = [(self.time_stamp >> d) & 0xFF for d in range(24, -1, -8)]
        b8_11 = [(self.SSRC >> d) & 0xFF for d in range(24, -1, -8)]
        self.header = bytes((b0, b1, b2, b3, *b4_7, *b8_11))
        #self.header = (b0 << 11) | (b1 << 10) | (b2_3 << 8) | (b4_7 << 4) | b8_11

    @classmethod
    def get_packet_from_bytes(cls, recv: bytes) :
        if (len(recv) < cls.HEADER_SIZE):
            raise InvalidRTPPacket(f"Receive packet is too short")
        header = recv[:cls.HEADER_SIZE]
        payload = recv[cls.HEADER_SIZE:]

        M = header[1] >> 7
        payload_type = header[1] & 0b01111111
        sequence_num = header[2] << 8 | header[3]
        time_stemp = header[4] << 24 | header[5] << 16 | header[6] << 8 | header[7]
        return cls(M, payload_type, sequence_num, time_stemp, payload)
    def get_packet(self) -> bytes:
        #print(self.header, self.payload)
        return bytes((*self.header, *self.payload))

if __name__ == "__main__":
    p = RTPPacket(sequence_num=0, time_stamp=123, payload=b'hello world')
    print(p.get_packet())
    pr = RTPPacket.get_packet_from_bytes(p.get_packet())
    print(pr.payload)

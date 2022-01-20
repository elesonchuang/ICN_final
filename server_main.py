from server.server import Server
HOST = '127.0.0.1'
PORT = 8888
if __name__ == '__main__':
    while True:
        server = Server(HOST, PORT)
        try:
            server.connect_client()
            server.setup()
            server.handle_rtsp_requests()
        except ConnectionError as e:
            ## server.server_state = server.STATE.TEARDOWN
            print(f"Connection reset: {e}")

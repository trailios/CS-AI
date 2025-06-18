import socket
from src.CSLBP.common import encrypt

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9999
PRE_SHARED_KEY = (
    "940fd2e68dcaf9bb9f8860d7fe069507bbd629f6db337a266d8dd2d9bae5c911"
    "a6c2ad70f96a54953d9f259b2296978b006d3439093d90276bb12ae432c30755"
)

class CSLBPClient:
    def __init__(self, host: str, port: int, key: str):
        self.server_address = (host, port)
        self.key = key
        self._connect()

    def _connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(self.server_address)
            print(f"Connected to {self.server_address}")
        except socket.error as e:
            self.sock.close()
            raise ConnectionError(f"Could not connect to server: {e}")

    def send_message(self, message: str) -> None:
        if not message:
            return

        try:
            data_bytes = message.encode('utf-8')
            encrypted_data = encrypt(data_bytes, self.key)
            length_prefix = len(encrypted_data).to_bytes(4, byteorder='big')
            self.sock.sendall(length_prefix + encrypted_data)
            print(f"Sent: '{message}'")
        except socket.error as e:
            print(f"Send failed ({e}), reconnecting...")
            self.sock.close()
            self._connect()
            self.send_message(message)

    def close(self) -> None:
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        finally:
            self.sock.close()
            print("Connection closed.")


def main():
    client = CSLBPClient(SERVER_HOST, SERVER_PORT, PRE_SHARED_KEY)
    print("CSLBP Client started. Type a message and press Enter to send. Type 'exit' to quit.")

    try:
        while True:
            msg = input("> ")
            if msg.lower() == 'exit':
                break
            client.send_message(msg)
    except (EOFError, KeyboardInterrupt):
        print("\nShutting down client.")
    finally:
        client.close()


if __name__ == "__main__":
    main()

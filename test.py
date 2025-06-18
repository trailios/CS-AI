from concurrent.futures import thread
import socket
import json
import uuid
import threading
import time
from src.CSLBP.common import encrypt, decrypt

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9999
PRE_SHARED_KEY = (
    "940fd2e68dcaf9bb9f8860d7fe069507bbd629f6db337a266d8dd2d9bae5c911"
    "a6c2ad70f96a54953d9f259b2296978b006d3439093d90276bb12ae432c30755"
)

lock = threading.Lock()

class CSLBPClient:
    def __init__(self, host, port, key):
        self.host = host
        self.port = port
        self.key = key.encode('utf-8')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.lock = threading.Lock()

    def send_task(self, task_payload: dict):
        message = json.dumps(task_payload).encode('utf-8')
        encrypted = encrypt(message, PRE_SHARED_KEY)
        length_prefix = len(encrypted).to_bytes(4, byteorder='big')
        with self.lock:
            self.sock.sendall(length_prefix + encrypted)

    def recv_response(self):
        with self.lock:
            prefix = self._recv_exact(4)
            if not prefix:
                raise ConnectionError("Connection closed while reading header")
            msg_len = int.from_bytes(prefix, byteorder='big')
            data = self._recv_exact(msg_len)
        decrypted = decrypt(data, PRE_SHARED_KEY)
        return json.loads(decrypted.decode('utf-8'))

    def _recv_exact(self, size: int) -> bytes:
        buf = b''
        while len(buf) < size:
            chunk = self.sock.recv(size - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def close(self):
        self.sock.close()

def task_worker(client: CSLBPClient, index: int):
    while True:
        task_id = f"CS-{uuid.uuid4()}"
        payload = {"id": task_id, "data": f"test message #{index}"}
        client.send_task(payload)
        print(f"[Task-{index}] Sent: {payload}")
        while True:
            try:
                response = client.recv_response()
                if response.get("id") == task_id:
                    with lock:
                        print(f"[Task-{index}] Response: {response}")
                    if response.get("status") == "finished":
                        break
            except Exception as e:
                print(f"[Task-{index}] Error: {e}")
                break

if __name__ == "__main__":
    client = CSLBPClient(SERVER_HOST, SERVER_PORT, PRE_SHARED_KEY)
    threads = []

    for i in range(5):
        t = threading.Thread(target=task_worker, args=(client, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    client.close()
    print("All tasks completed.")

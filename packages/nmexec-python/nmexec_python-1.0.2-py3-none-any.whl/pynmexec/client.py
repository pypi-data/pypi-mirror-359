import socket
import pickle
import struct
import time


class NmexecClient:
    def __init__(
        self,
        host: str,
        port: int,
        model_name: str,
        model_kwargs: dict,
        timeout: float = 30.0,
    ):
        self.host = host
        self.port = port
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.socket = None
        self._max_chunk_size = 1024 * 1024
        self.timeout = timeout

    def _check_socket_connected(self):
        """Check if socket is connected and ready for communication."""
        if self.socket is None:
            raise ConnectionError("Socket is not connected")

        try:
            self.socket.getpeername()
        except (OSError, socket.error):
            raise ConnectionError("Socket connection is closed")

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        conf = {
            "model_name": self.model_name,
            "model_kwargs": self.model_kwargs,
        }
        data = pickle.dumps(conf)
        self.socket.sendall(struct.pack("!I", len(data)))
        self.socket.sendall(data)

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None

    def exec_data(self, x):
        self._check_socket_connected()

        data = pickle.dumps(x)
        self.socket.sendall(struct.pack("!I", len(data)))

        for i in range(0, len(data), self._max_chunk_size):
            chunk = data[i: i + self._max_chunk_size]
            self.socket.sendall(chunk)

        rdata = b""
        start_time = time.time()
        while len(rdata) < 4:
            if time.time() - start_time > self.timeout:
                raise TimeoutError("Timeout waiting for response size")

            try:
                chunk = self.socket.recv(4 - len(rdata))
                if not chunk:
                    raise ConnectionError("Server closed the connection")
                rdata += chunk
            except socket.timeout:
                raise TimeoutError("Timeout waiting for response size")
            except (OSError, socket.error) as e:
                raise ConnectionError(f"Socket error while receiving: {e}")

        size = struct.unpack("!I", rdata)[0]

        rdata = b""
        start_time = time.time()
        while len(rdata) < size:
            if time.time() - start_time > self.timeout:
                raise TimeoutError("Timeout waiting for response data")

            try:
                chunk_size = min(size - len(rdata), self._max_chunk_size)
                chunk = self.socket.recv(chunk_size)
                if not chunk:
                    raise ConnectionError("Server closed the connection")
                rdata += chunk
            except socket.timeout:
                raise TimeoutError("Timeout waiting for response data")
            except (OSError, socket.error) as e:
                raise ConnectionError(f"Socket error while receiving: {e}")

        try:
            y = pickle.loads(rdata)
        except Exception as e:
            raise ValueError(f"Failed to deserialize response: {e}")

        return y

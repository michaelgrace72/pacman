from socket import *
import socket
import threading
import logging
import time
import sys

from protocol import PlayerServerProtocol
fp = PlayerServerProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                data = self.connection.recv(1024)
                if data:
                    d = data.decode()
                    hasil = fp.proses_string(d)
                    hasil = hasil + "\r\n\r\n"
                    self.connection.sendall(hasil.encode())
                else:
                    break
            except Exception as e:
                logging.error(f"Error processing client {self.address}: {e}")
                break
        self.connection.close()


class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.clients_lock = threading.Lock()  # Lock untuk client list
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            try:
                self.connection, self.client_address = self.my_socket.accept()
                logging.warning(f"connection from {self.client_address}")

                clt = ProcessTheClient(self.connection, self.client_address)
                clt.start()

                # Thread safe
                with self.clients_lock:
                    self.the_clients.append(clt)
                    self.the_clients = [c for c in self.the_clients if c.is_alive()]

            except Exception as e:
                logging.error(f"Error accepting connection: {e}")


def main():
    svr = Server(ipaddress='0.0.0.0', port=55555)
    svr.start()
    try:
        svr.join()
    except KeyboardInterrupt:
        logging.warning("Server shutting down...")


if __name__ == "__main__":
    main()

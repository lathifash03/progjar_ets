from socket import *
import socket
import threading
import logging
from file_protocol import ProtocolHandler  # Diubah ke ProtocolHandler

# Inisialisasi handler protokol
handler = ProtocolHandler()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"Connection from {self.address}")
        buffer = ""
        try:
            self.connection.settimeout(30.0)  # Tambahkan timeout
            
            while True:
                data = self.connection.recv(1024)  # Buffer diperbesar
                if not data:
                    break
                    
                buffer += data.decode()
                
                # Proses jika ada delimiter
                while "\r\n\r\n" in buffer:
                    request, buffer = buffer.split("\r\n\r\n", 1)
                    try:
                        response = handler.process_request(request) + "\r\n\r\n"
                        self.connection.sendall(response.encode())
                    except Exception as e:
                        error_msg = json.dumps({'status': 'ERROR', 'error': str(e)}) + "\r\n\r\n"
                        self.connection.sendall(error_msg.encode())
                        
        except socket.timeout:
            logging.warning(f"Connection timeout from {self.address}")
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {str(e)}")
        finally:
            self.connection.close()
            logging.warning(f"Connection closed from {self.address}")

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=6666):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"Server running on {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)  # Backlog diperbesar
        
        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"New connection from {client_address}")
                
                clt = ProcessTheClient(connection, client_address)
                clt.start()
                self.the_clients.append(clt)
                
                # Bersihkan thread yang sudah tidak aktif
                self.the_clients = [t for t in self.the_clients if t.is_alive()]
        except KeyboardInterrupt:
            logging.warning("Server shutting down...")
        except Exception as e:
            logging.error(f"Server error: {str(e)}")
        finally:
            self.my_socket.close()
            for client in self.the_clients:
                if client.is_alive():
                    client.connection.close()

def main():
    logging.basicConfig(level=logging.WARNING)
    svr = Server(ipaddress='0.0.0.0', port=6666)
    svr.start()

if __name__ == "__main__":
    main()

import socket
import json
import base64
import logging

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"Connecting to {server_address}")
        
        # Kirim command dan pastikan diakhiri dengan \r\n\r\n
        full_command = command_str + "\r\n\r\n"
        sock.sendall(full_command.encode())
        
        data_received = ""
        while True:
            data = sock.recv(1024)  # Buffer diperbesar
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                break
                
        if not data_received:
            logging.error("No data received from server")
            return {'status': 'ERROR', 'error': 'No response from server'}
            
        return json.loads(data_received.split("\r\n\r\n")[0])
        
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON response: {e}")
        return {'status': 'ERROR', 'error': 'Invalid server response'}
    except socket.error as e:
        logging.error(f"Socket error: {e}")
        return {'status': 'ERROR', 'error': str(e)}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {'status': 'ERROR', 'error': str(e)}
    finally:
        sock.close()

def remote_list():
    command_str = "list"  # Diubah ke lowercase
    hasil = send_command(command_str)
    if hasil.get('status') == 'OK':  # Lebih aman menggunakan .get()
        print("Daftar file:")
        for nmfile in hasil.get('data', []):
            print(f"- {nmfile}")
        return True
    else:
        print(f"Gagal: {hasil.get('error', 'Unknown error')}")
        return False

def remote_get(filename=""):
    if not filename:
        print("Nama file harus disertakan")
        return False
        
    command_str = f"get {filename}"  # Diubah ke lowercase
    hasil = send_command(command_str)
    if hasil.get('status') == 'OK':
        try:
            namafile = hasil.get('data_namafile', filename)
            isifile = base64.b64decode(hasil.get('data_file', ''))
            with open(namafile, 'wb') as fp:  # Menggunakan with untuk auto-close
                fp.write(isifile)
            print(f"File {namafile} berhasil didownload")
            return True
        except Exception as e:
            print(f"Gagal menyimpan file: {str(e)}")
            return False
    else:
        print(f"Gagal: {hasil.get('error', 'Unknown error')}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    server_address = ('172.16.16.101', 6666)
    remote_list()
    remote_get('donalbebek.jpg')

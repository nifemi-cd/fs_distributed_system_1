import socket
import time
import os
import json
import select

#host not defined so set to loobback address

DIR = "./files"
FILE_METADATA = "./files/files_resources.json"
SIZE = 1024  # Define the size of each chunk 


def set_non_blocking(sock):
    sock.setBlocking(False)


def handle_push(sock, filepath, username):
    print(f"Receiving file {filepath} from {username} on {sock.getpeername()}")
    
    sock.sendall(b"OK")
    file_size = int(sock.recv(1024).decode())
    if file_size:
        sock.sendall(b"OK")
    
    print(f"File {filepath} size: {file_size} bytes")
    data_recieved = 0

    with open(filepath, "wb") as f:
        while data_recieved < file_size:
            chunk = sock.recv(min(SIZE, file_size - data_recieved))
            f.write(chunk)
            data_recieved += len(chunk)

    print(f"File saved: {filepath}\n")


def handle_get(sock, filepath, username):
    print(f"Sending file {filepath} to {username} on {sock.getpeername()}")
    file_size = os.path.getsize(filepath)
    # print(file_size)
    sock.sendall(str(file_size).encode())  # Send the file size first

    if sock.recv(1024).decode() != "OK":
        return

    print(f"File {filepath} size: {file_size} bytes")
    
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
        print(f"File sent: {filepath}\n")
    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection closed by client while sending {filepath}\n")

def intialize():
    os.makedirs(DIR, exist_ok=True)
    if os.path.exists(FILE_METADATA):
        with open(FILE_METADATA, "r") as f:
            files_resources = json.load(f)
    else:
        files_resources = {}

    return files_resources

def save_file_info(files_resources):
    with open(FILE_METADATA, "w") as f:
        json.dump(files_resources, f, indent=4)


def process_client_commands(sock, clients, sockets, files_resources):
    try:
        data = sock.recv(1024).decode().strip()
        if not data:
            sock.sendall(b"Connection closed.\n")
            cleanup(sock, clients, sockets)
            return

        command, *args = data.split(maxsplit=1)
        username = clients.get(sock, None)

        if command == "DELETE":
            if not username:
                sock.sendall(b"You must login first using LOGIN <username>.\n")
                return
            filename = args[0]
            filepath = os.path.join(DIR, filename)
            if filename in files_resources and files_resources[filename]["owner"] == username:
                if os.path.exists(f"files/{filename}"):
                    os.remove(filepath)
                    del files_resources[filename]
                    save_file_info(files_resources)
                    print(f"File {filename} deleted by {username}\n")
                    sock.sendall(b"File deleted.\n")
                else:
                    sock.sendall(b"File not found.\n")
            else:
                sock.sendall(b"Permission denied. You are not the owner of this file.\n")

        elif command == "LIST":
            if not username:
                sock.sendall(b"You must login first with a username.\n")
                return
            if files_resources:
                response = "\n".join(
                    f"{name} - {meta['size']} bytes - Uploaded by {meta['owner']} on {meta['timestamp']}"
                    for name, meta in files_resources.items()
                )
                sock.sendall(response.encode())
            else:
                sock.sendall(b"No files available.\n")

        elif command == "GET":
            if not username:
                sock.sendall(b"You must login first using LOGIN <username>.\n")
                return
            
            
            filename = args[0]
            filepath = os.path.join(DIR, filename)
            if os.path.exists(f"files/{filename}"):
                handle_get(sock, filepath, username)
            else:
                sock.sendall(b"File not found.\n")

        elif command == "PUSH":
            if not username:
                sock.sendall(b"You must login first using LOGIN <username>.\n")
                return
            filename = args[0]
            filepath = os.path.join(DIR, filename)
            handle_push(sock, filepath, username)
            file_size = os.path.getsize(filepath)
            files_resources[filename] = {
                "owner": username,
                "timestamp": time.ctime(),
                "size": file_size
            }
            save_file_info(files_resources)
            sock.sendall("File uploaded successfully.\n".encode())
        
        elif command == "LOGIN":
            if not args:
                sock.sendall(b"LOGIN command requires a username.\n")
                return
            else:
                username = args[0]
                clients[sock] = username
                sock.sendall(f"OK".encode())
                print(f"User {username} logged in from {sock.getpeername()}\n")

        elif command == "LOGOUT":
            print(f"User {username} logged out from {sock.getpeername()}\n")
            
        
        else:
            sock.send(b"Unknown command.\n")
    except Exception as e:
        try:
            peer = sock.getpeername()
        except:
            peer = "disconnected"
        print(f"Error handling client {peer}: {e}\n")
        sock.sendall(b"Error processing request.\n")
        cleanup(sock, clients, sockets)


def cleanup(sock, clients, sockets):
    try:
        if sock in sockets:
            sockets.remove(sock)
        if sock in clients:
            del clients[sock]
        sock.close()
    except OSError as e:
        print(f"Error cleaning up socket: {e}\n")
    except KeyError as e:
        print("Socket not found in clients dictionary: {e}\n")
    return

def main():
    files_resources = intialize()
    HOST = '0.0.0.0'
    # HOST = '0.0.0.0' #loop back address
    PORT = 8286
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()
    print("Server listening on {}:{}\n".format(HOST, PORT))

    sockets = [serverSocket, ] #maintain a list of sockets
    clients = {}  #also the client dictionary

    while True:

        try:
            myReadables, _, _ = select.select(sockets, [], [])
            for s in myReadables:
                if s is serverSocket:
                    sock, addr = serverSocket.accept()
                    # set_non_blocking(sock)
                    print(f"Connected by {addr}")
                    sockets.append(sock)
                    clients[sock] = {"username": None, "address": addr}  # add client to clients
                else:
                    process_client_commands(s, clients, sockets, files_resources)
        except socket.timeout:
            print("Socket timeout, no data received.\n")
            cleanup(s, clients, sockets)
            break
        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting now\n")
            cleanup(s, clients, sockets)
            break
        except Exception as e:
            print(f"Error: {e}\n")
            cleanup(s, clients, sockets)
            break

if __name__ == "__main__":
    main()
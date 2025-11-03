import socket
import os

HOST = '127.0.0.1' #change to your server address as needed
PORT = 8286
SIZE = 1024

#created client as a class to allow for multiple instances to be created, to simulate multiple clients
#and to allow for easy access to the socket and other variables

class TreeDriveClient:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        self.sock.connect((self.host, self.port))

    def push_file(self, filename):
        if not os.path.exists(filename):
            print("File does not exist.")
            return
        basename = os.path.basename(filename)
        self.sock.sendall(f"PUSH {basename}".encode())
        resp = self.sock.recv(1024).decode()
        if resp.strip() != "OK":
            print("Server did not accept PUSH:", resp)
            return
        filesize = os.path.getsize(filename)
        # print(filesize)

        self.sock.sendall(str(filesize).encode())
        if self.sock.recv(1024).decode().strip() != "OK":
            return
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(SIZE)
                if not chunk:
                    break
                self.sock.sendall(chunk)
        # print("File uploaded.")
        print(self.sock.recv(1024).decode())
        

    def get_file(self, filename):
        self.sock.sendall(f"GET {filename}".encode())
        resp = self.sock.recv(1024)
        # if resp != "OK":
        #     return
        if resp.decode() == "File not found.\n":
            print(resp.decode())
            return
        filesize = int(resp.decode())
        self.sock.sendall("OK".encode())
        # print(filesize)
        

        try:
            
            with open(filename, "wb") as f:
                received = 0
                while received < filesize:
                    chunk = self.sock.recv(min(SIZE, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            print("File downloaded.")
        except ValueError as e:
            print("Error in file size:", e)
            return
        except UnicodeDecodeError as e:
            print("Error in file data:", e)
            return

    def approve_login(self):
        while True:
            username = input("Input Username to Login: ").strip()
            self.sock.sendall(f"LOGIN {username}".encode())
            resp = self.sock.recv(1024).decode()
            if resp == "OK":
                break

    def start_client(self):
        self.connect_to_server()
        self.approve_login()

        while True:
            cmd = input("\nCommand--> ").strip()
            if cmd.upper().startswith("PUSH "):
                filename = cmd.split(maxsplit=1)[1]
                self.push_file(filename)
            elif cmd.upper().startswith("GET "):
                filename = cmd.split(maxsplit=1)[1]
                self.get_file(filename)
            elif cmd.upper() == "LIST":
                self.sock.sendall("LIST".encode())
                resp = self.sock.recv(4096).decode()
                print(resp)
            elif cmd.upper().startswith("DELETE "):
                filename = cmd.split(maxsplit=1)[1]
                self.sock.sendall(f"DELETE {filename}".encode())
                resp = self.sock.recv(1024).decode()
                print(resp)
            elif cmd.lower().startswith("cd "):
                path = cmd.split(maxsplit=1)[1]
                try:
                    os.chdir(path)
                except Exception as e:
                    print(f"cd: {e}")
            elif cmd.lower() == "ls":
                for entry in os.listdir(os.getcwd()):
                    print(entry)
            elif cmd.upper() in ("EXIT", "QUIT", "LOGOUT", "DONE"):
                self.sock.sendall("LOGOUT".encode())
                self.sock.close()
                break
            else:
                print("Unknown command.")

if __name__ == "__main__":
    client = TreeDriveClient()
    client.start_client()
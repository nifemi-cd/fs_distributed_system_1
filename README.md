# fs_distributed_system_1

## Overview
TreeDrive is a simple client-server file sharing system that allows multiple users to upload, download, list, and delete files on a central server. The system is implemented in Python and supports concurrent client connections.

---

## Instructions

### 1. Starting the Server

1. Open a terminal on the server machine.
2. Navigate to the project directory:
   ```bash
   cd /path/to/your/project
   ```
3. Start the server:
   ```bash
   python3 tree_drive_server.py
   ```
4. The server will listen for incoming client connections on the configured host and port (default: 0.0.0.0:8286).

---

### 2. Starting the Client

1. Open a terminal on the client machine.
2. Navigate to the project directory:
   ```bash
   cd /path/to/your/project
   ```
3. Start the client:
   ```bash
   python3 tree_drive_client.py
   ```
4. When prompted, enter your username to log in.

---

## 3. Interacting with the System

After logging in, you can use the following commands at the client prompt:

- `PUSH <filename>`: Upload a file from the client to the server.
- `GET <filename>`: Download a file from the server to the client.
- `LIST`: List all files available on the server, including metadata (owner, size, upload time).
- `DELETE <filename>`: Delete a file from the server (only if you are the owner).
- `cd <path>`: Change the local directory on the client.
- `ls`: List files in the current local client directory.
- `EXIT`, `QUIT`, `LOGOUT`, or `DONE`: Log out and close the client.

**Example session:**
```
Input Username to Login: alice
Command--> PUSH myfile.txt
Command--> LIST
Command--> GET myfile.txt
Command--> DELETE myfile.txt
Command--> LOGOUT
```

---

## 4. Additional Features / Notes

- **Multi-client support:** The server can handle multiple clients concurrently using Python's `select` module.
- **File metadata:** The server maintains a JSON file with metadata for all uploaded files (owner, size, upload time).
- **Ownership enforcement:** Only the user who uploaded a file can delete it.
- **Local navigation:** The client supports `cd` and `ls` for local directory management.
- **Graceful error handling:** The system provides informative error messages for invalid commands, missing files, and permission issues.

---

## 5. Bonus Functionality / Notes
- **Customizable server address/port:** You can change the `HOST` and `PORT` variables in the client and server scripts to match your deployment.

---

## 6. Troubleshooting
- Ensure the server is running before starting any clients.
- Make sure the file you want to upload exists in the client's current directory.
- If you encounter connection errors, check that the `HOST` and `PORT` match on both server and client.

---

## 7. File List
- `tree_drive_server.py`: The main server script.
- `tree_drive_client.py`: The main client script.
- `files/`: Directory where server-side files are stored.
- `files_resources.json`: Server-side file metadata.

---


import socket

# Target machine IP and port
Host_IP = "192.168.1.195" 
Host_Port = 5000
 
 
# Establish socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect((Host_IP, Host_Port)) 
 
# sending command function, responses are set to be denoted by <<END>>
def send_command(command):
    client.sendall(command.encode())

    if command.startswith("cmd:"): 
        data = b""
        while b"<<END>>" not in data:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk 

        data = data.replace(b"<<END>>", b"")
        print("Response:\n" + data.decode())


# Possible commands list
while True:
    text = input("Type command: ")

    # Break connection with target
    if text.lower() == "exit": 
        break 

    # Open url 
    elif text.startswith("browser "):
        url = text.split(" ", 1)[1]
        send_command(f"browser:{url}")

    # Execute command line command
    elif text.startswith("cmd "):
        command = text.split(" ", 1)[1]
        send_command(f"cmd:{command}")

    # Simulated key press
    elif text.startswith("key "):
        key = text.split(" ", 1)[1]
        send_command(f"key:{key}")

    # Simulate complex key press
    elif text.startswith("hotkey "):
        keys = text.split(" ", 1)[1]
        send_command(f"hotkey:{keys.replace(' ', '+')}")

    # Type out text (no prefix needed)
    else:
        send_command(text)

client.close()

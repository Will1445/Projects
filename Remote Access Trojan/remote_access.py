import socket

HOST = "192.168.1.129"  # Ubuntu's IP address
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def send_command(command):
    client.sendall(command.encode())
    if command.startswith("cmd:"):
        response = client.recv(4096).decode()  # Get command output
        print(f"Response:\n{response}")

while True:
    text = input("Type command: ")

    if text.lower() == "exit":
        break

    elif text.startswith("browser "):
        url = text.split(" ", 1)[1]
        send_command(f"browser:{url}")

    elif text.startswith("cmd "):
        command = text.split(" ", 1)[1]
        send_command(f"cmd:{command}")

    elif text.startswith("key "):
        key = text.split(" ", 1)[1]
        send_command(f"key:{key}")

    elif text.startswith("hotkey "):
        keys = text.split(" ", 1)[1]
        send_command(f"hotkey:{keys.replace(' ', '+')}")

    else:
        send_command(text)

client.close()

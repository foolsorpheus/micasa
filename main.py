import socket
import json
import struct

from flask import Flask

app = Flask(__name__)

TCP_IP = "192.168.1.117"
TCP_PORT = 9999

payload = {"system":{"get_sysinfo":{}}}


# TP-Link Kasa XOR cipher
def encrypt(text: str) -> bytes:
    key = 0xAB
    result = bytearray()

    for b in text.encode("utf-8"):
        cipher = b ^ key
        key = cipher
        result.append(cipher)

    return bytes(result)


def decrypt(data: bytes) -> str:
    key = 0xAB
    result = bytearray()

    for b in data:
        plain = b ^ key
        key = b
        result.append(plain)

    return result.decode("utf-8")


def recv_exact(sock: socket.socket, size: int) -> bytes:
    """Read exactly N bytes from TCP"""
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Socket closed early")
        data += chunk
    return data

def send_command(cmd_dict):
    """Helper to send a command and return the response"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((TCP_IP, TCP_PORT))
        
        encrypted = encrypt(json.dumps(cmd_dict))
        s.sendall(struct.pack(">I", len(encrypted)) + encrypted)
        
        header = recv_exact(s, 4)
        response_length = struct.unpack(">I", header)[0]
        encrypted_response = recv_exact(s, response_length)
        return json.loads(decrypt(encrypted_response))

def set_state(state):
    return send_command({"system": {"set_relay_state": {"state": state}}})

def turn_on():
    return set_state(1)

def turn_off():
    return set_state(0)

def toggle():
    """Get the current state of the lamp and set it to the opposite"""
    info = send_command(payload)
    relay_state = info["system"]["get_sysinfo"]["relay_state"]
    new_state = 1 if relay_state == 0 else 0
    set_state(new_state)
    return new_state

@app.route('/toggle', methods=['POST'])
def api_toggle():
    new_state = toggle()
    return {"status": "success", "new_state": new_state}

@app.route('/on', methods=['POST'])
def api_on():
    turn_on()
    return {"status": "success", "state": 1}

@app.route('/off', methods=['POST'])
def api_off():
    turn_off()
    return {"status": "success", "state": 0}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
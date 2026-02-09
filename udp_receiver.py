import socket
import struct

UDP_IP = "0.0.0.0"   # listen on all interfaces
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening for UDP packets...")

while True:
    data, addr = sock.recvfrom(1024)

    if len(data) == 48:
        x, y, z, roll, pitch, yaw = struct.unpack('6d', data)
        print(f"x={x:.2f}, y={y:.2f}, z={z:.2f}, "
              f"φ={roll:.2f}, θ={pitch:.2f}, ψ={yaw:.2f}")
    else:
        print(f"Unexpected packet size: {len(data)} bytes")

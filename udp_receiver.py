import socket
import struct
import sys #for keyboard interrupt
import matplotlib.pyplot as plt #for plots
UDP_IP = "0.0.0.0"   # listen on all interfaces
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #explain better what this command does
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.5) #if for some reason transmission stops, it will exit recieve mode

print("Listening for UDP packets...")

counter = 0
t_data = []
x_data = []
y_data = []
z_data = []

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue #allows The keyboard exception to be "caught" 
    
        if len(data) == 56:
            t, x, y, z, roll, pitch, yaw = struct.unpack('7d', data)  
            t_data.append(t)
            x_data.append(x)
            y_data.append(y)
            z_data.append(z)
            counter += 1
            if counter % 10 == 0:   # print at 10 Hz instead of 100 Hz
                print(f"x={x:.2f}, y={y:.2f}, z={z:.2f}, " f"φ={roll:.2f}, θ={pitch:.2f}, ψ={yaw:.2f}")
        else:
            print(f"Unexpected packet size: {len(data)} bytes")

except KeyboardInterrupt:
    print("\nStopping UDP receiver cleanly...")
    sock.close()
    # Plot after simulation ends
    plt.figure()
    plt.plot(t_data, x_data, label="x")
    plt.plot(t_data, y_data, label="y")
    plt.plot(t_data, z_data, label="z")
    plt.xlabel("Time [s]")
    plt.ylabel("Position")
    plt.title("Position vs Time")
    plt.legend()
    plt.grid(True)
    plt.show()

    sys.exit(0)

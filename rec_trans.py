import socket
import struct
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.style.use('dark_background')
plt.ion()

# ===============================
# UDP SETTINGS
# ===============================

# Send to Simulink
SIMULINK_IP = "127.0.0.1"
SIMULINK_PORT = 9090

# Listen from Simulink
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

dt = 0.01

# Create send socket
sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create receive socket
sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_rx.bind((UDP_IP, UDP_PORT))
sock_rx.settimeout(0.001)

print("Streaming + Listening... Press Ctrl+C to stop.")

# ===============================
# Plot Setup
# ===============================

t_data, x_data, y_data, z_data = [], [], [], []

fig, ax = plt.subplots()
line_x, = ax.plot([], [], label="x")
line_y, = ax.plot([], [], label="y")
line_z, = ax.plot([], [], label="z")

ax.set_xlabel("Time [s]")
ax.set_ylabel("Position")
ax.legend()
ax.grid(True)

fig3d = plt.figure()
ax3d = fig3d.add_subplot(111, projection='3d')
line3d, = ax3d.plot([], [], [], label="Trajectory")

ax3d.set_xlabel("X")
ax3d.set_ylabel("Y")
ax3d.set_zlabel("Z")
ax3d.legend()

# ===============================
# Main Loop
# ===============================

t0 = time.time()
counter = 0

try:
    while True:

        # ---------- SEND REFERENCE ----------
        t = time.time() - t0

        x_ref = 5 if t < 6 else 10
        y_ref = 7 if t < 6 else 14
        z_ref = 7 if t < 12 else 19

        packet_tx = struct.pack('<3d', x_ref, y_ref, z_ref)
        sock_tx.sendto(packet_tx, (SIMULINK_IP, SIMULINK_PORT))

        # ---------- RECEIVE STATE ----------
        try:
            data, addr = sock_rx.recvfrom(1024)
            if len(data) == 56:
                t_sim, x, y, z, roll, pitch, yaw = struct.unpack('<7d', data)

                t_data.append(t_sim)
                x_data.append(x)
                y_data.append(y)
                z_data.append(z)

                if counter % 25 == 0:

                    # 2D plot
                    line_x.set_data(t_data, x_data)
                    line_y.set_data(t_data, y_data)
                    line_z.set_data(t_data, z_data)
                    ax.relim()
                    ax.autoscale_view()

                    # 3D plot
                    line3d.set_data(x_data, y_data)
                    line3d.set_3d_properties(z_data)

                    ax3d.set_xlim(min(x_data), max(x_data))
                    ax3d.set_ylim(min(y_data), max(y_data))
                    ax3d.set_zlim(min(z_data), max(z_data))

                    plt.pause(0.001)

                counter += 1

        except socket.timeout:
            pass

        time.sleep(dt)

except KeyboardInterrupt:
    print("Stopping cleanly...")
    sock_tx.close()
    sock_rx.close()
    plt.ioff()
    plt.show()
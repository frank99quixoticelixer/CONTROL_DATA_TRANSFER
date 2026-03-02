# Trajectory generation + UDP transmission

import numpy as np
import time
import socket
import struct
import matplotlib.pyplot as plt

# =============================
# UDP CONFIGURATION (to Simulink)
# =============================
SIMULINK_IP = "127.0.0.1"   # same PC
SIMULINK_PORT = 9090       # must match Simulink local port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# =============================
# Simulation / Sampling Settings
# =============================
dt = 0.01
t_final = 20

t = np.arange(0, t_final, dt)

# =============================
# Step Definitions
# =============================

x_ref = np.where(t < 6, 5, 10)
y_ref = np.where(t < 6, 7, 14)
z_ref = np.where(t < 12, 7, 19)

# =============================
# STREAM TO SIMULINK
# =============================

print("Streaming references to Simulink...")

for i in range(len(t)):

    # Pack 3 doubles → 24 bytes
    packet = struct.pack('<3d', x_ref[i], y_ref[i], z_ref[i])

    sock.sendto(packet, (SIMULINK_IP, SIMULINK_PORT))

    time.sleep(dt)   # maintain 0.01 s rate

print("Streaming finished.")

sock.close()

import socket
import struct
import sys #for keyboard interrupt
import matplotlib.pyplot as plt #for plots
from mpl_toolkits.mplot3d import Axes3D # 3d plot
plt.style.use('dark_background')
def set_equal_3d(ax, x, y, z):
    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)
    zmin, zmax = min(z), max(z)

    # Prevent zero range
    if xmin == xmax:
        xmin -= 0.1
        xmax += 0.1
    if ymin == ymax:
        ymin -= 0.1
        ymax += 0.1
    if zmin == zmax:
        zmin -= 0.1
        zmax += 0.1

    x_range = xmax - xmin
    y_range = ymax - ymin
    z_range = zmax - zmin
    max_range = max(x_range, y_range, z_range)

    mid_x = (xmax + xmin) / 2
    mid_y = (ymax + ymin) / 2
    mid_z = (zmax + zmin) / 2

    ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
    ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
    ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
    return None

plt.ion() # Interactive plots
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

# Live plot for position
fig, ax = plt.subplots()
line_x, = ax.plot([], [], label="x")
line_y, = ax.plot([], [], label="y")
line_z, = ax.plot([], [], label="z")

ax.set_xlabel("Time [s]")
ax.set_ylabel("Position")
ax.set_title("Live Position vs Time")
ax.legend()
ax.grid(True)

# Live 3D trajectory plot
fig3d = plt.figure()
ax3d = fig3d.add_subplot(111, projection='3d')
line3d, = ax3d.plot([], [], [], label="Trajectory")

ax3d.set_xlabel("X")
ax3d.set_ylabel("Y")
ax3d.set_zlabel("Z")
ax3d.set_title("Live 3D Trajectory")
ax3d.legend()


try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue #allows The keyboard exception to be "caught" 
    
        if len(data) == 56: #only if the packet recieved matches the size of the data
            t, x, y, z, roll, pitch, yaw = struct.unpack('7d', data)  
            # store streamed data
            t_data.append(t)
            x_data.append(x)
            y_data.append(y)
            z_data.append(z)
            # Update live plot every few samples
            if counter % 5 == 0:
                line_x.set_data(t_data, x_data)
                line_y.set_data(t_data, y_data)
                line_z.set_data(t_data, z_data)

                ax.relim()
                ax.autoscale_view()
                # --- 3D trajectory plot ---
                line3d.set_data(x_data, y_data)
                line3d.set_3d_properties(z_data)

                # Manual autoscale
                if len(x_data) > 1:
                    set_equal_3d(ax3d, x_data, y_data, z_data)
                #ax3d.set_xlim(min(x_data), max(x_data))
                #ax3d.set_ylim(min(y_data), max(y_data))
                #ax3d.set_zlim(min(z_data), max(z_data))
            counter += 1
            #if counter % 10 == 0:   # print at 10 Hz instead of 100 Hz
                #print(f"x={x:.2f}, y={y:.2f}, z={z:.2f}, " f"φ={roll:.2f}, θ={pitch:.2f}, ψ={yaw:.2f}")
        else:
            print(f"Unexpected packet size: {len(data)} bytes")
        plt.pause(0.001)

except KeyboardInterrupt:
    print("\nStopping UDP receiver cleanly...")
    sock.close()

    plt.ioff() # turn interactive mode
    # Close the live updating figure
    plt.close(fig)


    # Create final static plot
    fig_final, ax_final = plt.subplots()
    ax_final.plot(t_data, x_data, label="x")
    ax_final.plot(t_data, y_data, label="y")
    ax_final.plot(t_data, z_data, label="z")

    ax_final.set_xlabel("Time [s]")
    ax_final.set_ylabel("Position")
    ax_final.set_title("Final Position vs Time")
    ax_final.legend()
    ax_final.grid(True)
    plt.show()
    
    # Final static 3D trajectory
    fig3d_final = plt.figure()
    ax3d_final = fig3d_final.add_subplot(111, projection='3d')

    ax3d_final.plot(x_data, y_data, z_data)
    ax3d_final.set_xlabel("X")
    ax3d_final.set_ylabel("Y")
    ax3d_final.set_zlabel("Z")
    ax3d_final.set_title("Final 3D Trajectory")

    plt.show(block = True)
    sys.exit(0)



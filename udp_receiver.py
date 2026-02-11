import socket
import struct
import sys #for keyboard interrupt
import matplotlib.pyplot as plt #for plots
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

# Live plot
fig, ax = plt.subplots()
line_x, = ax.plot([], [], label="x")
line_y, = ax.plot([], [], label="y")
line_z, = ax.plot([], [], label="z")

ax.set_xlabel("Time [s]")
ax.set_ylabel("Position")
ax.set_title("Live Position vs Time")
ax.legend()
ax.grid(True)

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

                plt.pause(0.001)
            counter += 1
            #if counter % 10 == 0:   # print at 10 Hz instead of 100 Hz
                #print(f"x={x:.2f}, y={y:.2f}, z={z:.2f}, " f"φ={roll:.2f}, θ={pitch:.2f}, ψ={yaw:.2f}")
        else:
            print(f"Unexpected packet size: {len(data)} bytes")

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

    sys.exit(0)

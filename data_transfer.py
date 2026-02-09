import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  

# Rotation Matrix 
def Rot_Matrix(phi, theta, psi):
    # Roll (x-axis)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(phi), -np.sin(phi)],
        [0, np.sin(phi),  np.cos(phi)]
    ])

    # Pitch (y-axis)
    Ry = np.array([
        [ np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    # Yaw (z-axis)
    Rz = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi),  np.cos(psi), 0],
        [0, 0, 1]
    ])

    return Rz @ Ry @ Rx

# =========================
# LOAD CSV
# =========================
df = pd.read_csv("quadcopter_sim_log.csv")
L = 0.25  # arm length [m]
# Quad geometry in BODY frame
quad_body = np.array([
    [ L,  0,  0],   # front
    [-L,  0,  0],   # back
    [ 0,  L,  0],   # right
    [ 0, -L,  0],   # left
])
# =========================
# EXTRACT COLUMNS
# =========================
t = df["time"]
x = df["x"]
y = df["y"]
z = df["z"]

phi = df["phi"]
theta = df["theta"]
psi = df["psi"]
# =========================
# POSITION PLOT
# =========================
plt.figure()
plt.plot(t, x, label="x")
plt.plot(t, y, label="y")
plt.plot(t, z, label="z")
plt.xlabel("Time [s]")
plt.ylabel("Position [m]")
plt.title("Quadcopter Position")
plt.legend()
plt.grid()
# =========================
# ANGLES PLOT
# =========================
plt.figure()
plt.plot(t, phi, label="roll (phi)")
plt.plot(t, theta, label="pitch (theta)")
plt.plot(t, psi, label="yaw (psi)")
plt.xlabel("Time [s]")
plt.ylabel("Angle [rad]")
plt.title("Quadcopter Attitude")
plt.legend()
plt.grid()

# =========================
# 3D TRAJECTORY PLOT
# =========================
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

ax.plot(x, y, z, linewidth=2)

ax.set_xlabel("X [m]")
ax.set_ylabel("Y [m]")
ax.set_zlabel("Z [m]")
ax.set_title("Quadcopter 3D Trajectory")

# Equal axis scaling
max_range = max(
    x.max() - x.min(),
    y.max() - y.min(),
    z.max() - z.min()
) / 2.0

mid_x = (x.max() + x.min()) / 2
mid_y = (y.max() + y.min()) / 2
mid_z = (z.max() + z.min()) / 2

ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

ax.grid()


# Create quad arms (empty at start)
arm1, = ax.plot([], [], [], lw=6, color="red")
arm2, = ax.plot([], [], [], lw=6, color="blue")

# Trajectory line
traj, = ax.plot([], [], [], lw=2, color="black")

# =========================
# ANIMATION LOOP
# =========================
plt.show(block=False)

for i in range(len(x)):
    # Rotation
    R = Rot_Matrix(phi.iloc[i], theta.iloc[i], psi.iloc[i])

    # Rotate + translate quad
    quad_world = (R @ quad_body.T).T
    quad_world += np.array([x.iloc[i], y.iloc[i], z.iloc[i]])

    # Arm 1 (front-back)
    arm1.set_data(
        [quad_world[0, 0], quad_world[1, 0]],
        [quad_world[0, 1], quad_world[1, 1]]
    )
    arm1.set_3d_properties(
        [quad_world[0, 2], quad_world[1, 2]]
    )

    # Arm 2 (left-right)
    arm2.set_data(
        [quad_world[2, 0], quad_world[3, 0]],
        [quad_world[2, 1], quad_world[3, 1]]
    )
    arm2.set_3d_properties(
        [quad_world[2, 2], quad_world[3, 2]]
    )

    # Trajectory up to now
    traj.set_data(x.iloc[:i], y.iloc[:i])
    traj.set_3d_properties(z.iloc[:i])

    plt.pause(0.1)


plt.show()

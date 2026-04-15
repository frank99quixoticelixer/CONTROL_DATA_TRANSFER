import socket
import struct
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matlab.engine
import threading
import sys

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

dt = 0.01  # 100Hz control loop

class SimulinkUDPController:
    def __init__(self):
        # MATLAB Engine
        self.eng = None
        self.matlab_running = False
        self.simulation_running = False
        
        # UDP Sockets
        self.sock_tx = None
        self.sock_rx = None
        
        # Data storage
        self.t_data = []
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.roll_data = []
        self.pitch_data = []
        self.yaw_data = []
        
        # Timing
        self.t0 = None
        self.counter = 0
        
        # Plot setup
        self.setup_plots()
        
    def setup_plots(self):
        """Initialize the plots"""
        # 2D position plot
        self.fig, self.ax = plt.subplots()
        self.line_x, = self.ax.plot([], [], label="X", color='red')
        self.line_y, = self.ax.plot([], [], label="Y", color='green')
        self.line_z, = self.ax.plot([], [], label="Z", color='blue')
        
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Position [m]")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # 3D trajectory plot
        self.fig3d = plt.figure()
        self.ax3d = self.fig3d.add_subplot(111, projection='3d')
        self.line3d, = self.ax3d.plot([], [], [], 'cyan', label="Trajectory", linewidth=2)
        self.current_pos, = self.ax3d.plot([0], [0], [0], 'ro', markersize=8, label="Current")
        
        self.ax3d.set_xlabel("X [m]")
        self.ax3d.set_ylabel("Y [m]")
        self.ax3d.set_zlabel("Z [m]")
        self.ax3d.legend()
        
        # Attitude plot (optional)
        self.fig_att, self.ax_att = plt.subplots()
        self.line_roll, = self.ax_att.plot([], [], label="Roll", color='orange')
        self.line_pitch, = self.ax_att.plot([], [], label="Pitch", color='purple')
        self.line_yaw, = self.ax_att.plot([], [], label="Yaw", color='brown')
        
        self.ax_att.set_xlabel("Time [s]")
        self.ax_att.set_ylabel("Angle [rad]")
        self.ax_att.legend()
        self.ax_att.grid(True, alpha=0.3)
        
    def start_matlab(self):
        """Start MATLAB engine and open Simulink model"""
        print(" Starting MATLAB engine...")
        self.eng = matlab.engine.start_matlab()
        
        # Navigate to thesis directory
        thesis_path = r"C:\Users\Thetw\Documents\UNAQ\TESIS\CONTROL_DATA_TRANSFER"
        self.eng.cd(thesis_path)
        print(f" Working directory: {thesis_path}")
        
        # Open Simulink model
        model_name = "CONTROL_F2"
        try:
            self.eng.open_system(model_name, nargout=0)
            print(f" Opened Simulink model: {model_name}")
            self.matlab_running = True
            return True
        except Exception as e:
            print(f" Error opening model: {e}")
            return False
    
    def start_simulation(self):
        """Start the Simulink simulation"""
        if not self.matlab_running:
            print(" MATLAB not running")
            return False
        
        try:
            # Set simulation time (adjust as needed)
            self.eng.set_param("CONTROL_F2", "StopTime", "100", nargout=0)
            
            # Start simulation (non-blocking)
            self.eng.set_param("CONTROL_F2", "SimulationCommand", "start", nargout=0)
            print(" Simulation started")
            self.simulation_running = True
            return True
        except Exception as e:
            print(f" Error starting simulation: {e}")
            return False
    
    def setup_udp(self):
        """Initialize UDP sockets"""
        try:
            # Create send socket
            self.sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Create receive socket
            self.sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_rx.bind((UDP_IP, UDP_PORT))
            self.sock_rx.settimeout(0.001)
            
            print(f" UDP: Sending to port {SIMULINK_PORT}, Receiving on port {UDP_PORT}")
            return True
        except Exception as e:
            print(f" UDP setup error: {e}")
            return False
    
    def get_reference(self, t):
        """Generate reference trajectory based on time"""
        # Waypoint 1: first 6 seconds
        if t < 6:
            x_ref = 5.0
            y_ref = 7.0
            z_ref = 7.0
        # Waypoint 2: 6-12 seconds
        elif t < 12:
            x_ref = 10.0
            y_ref = 14.0
            z_ref = 7.0
        # Waypoint 3: after 12 seconds
        else:
            x_ref = 10.0
            y_ref = 14.0
            z_ref = 19.0
            
        return x_ref, y_ref, z_ref
    
    def update_plots(self):
        """Update all plots"""
        # 2D position plot
        self.line_x.set_data(self.t_data, self.x_data)
        self.line_y.set_data(self.t_data, self.y_data)
        self.line_z.set_data(self.t_data, self.z_data)
        self.ax.relim()
        self.ax.autoscale_view()
        
        # 3D plot
        if len(self.x_data) > 1:
            self.line3d.set_data(self.x_data, self.y_data)
            self.line3d.set_3d_properties(self.z_data)
            
            # Update current position marker
            self.current_pos.set_data([self.x_data[-1]], [self.y_data[-1]])
            self.current_pos.set_3d_properties([self.z_data[-1]])
            
            # Auto-scale 3D plot
            max_range = max([
                max(self.x_data) - min(self.x_data),
                max(self.y_data) - min(self.y_data),
                max(self.z_data) - min(self.z_data)
            ]) / 2.0
            
            mid_x = (max(self.x_data) + min(self.x_data)) / 2
            mid_y = (max(self.y_data) + min(self.y_data)) / 2
            mid_z = (max(self.z_data) + min(self.z_data)) / 2
            
            self.ax3d.set_xlim(mid_x - max_range, mid_x + max_range)
            self.ax3d.set_ylim(mid_y - max_range, mid_y + max_range)
            self.ax3d.set_zlim(mid_z - max_range, mid_z + max_range)
        
        # Attitude plot (if we have attitude data)
        if self.roll_data:
            self.line_roll.set_data(self.t_data, self.roll_data)
            self.line_pitch.set_data(self.t_data, self.pitch_data)
            self.line_yaw.set_data(self.t_data, self.yaw_data)
            self.ax_att.relim()
            self.ax_att.autoscale_view()
        
        plt.pause(0.001)
    
    def run_control_loop(self):
        """Main control loop"""
        print(" Starting control loop. Press Ctrl+C to stop.")
        print(" MATLAB will remain open after stopping.")
        
        self.t0 = time.time()
        
        try:
            while True:
                loop_start = time.time()
                
                # ---------- SEND REFERENCE ----------
                t = time.time() - self.t0
                x_ref, y_ref, z_ref = self.get_reference(t)
                
                # Pack and send 3 doubles (24 bytes)
                packet_tx = struct.pack('<3d', x_ref, y_ref, z_ref)
                self.sock_tx.sendto(packet_tx, (SIMULINK_IP, SIMULINK_PORT))
                
                # ---------- RECEIVE STATE ----------
                try:
                    data, addr = self.sock_rx.recvfrom(1024)
                    
                    # Check data length (7 doubles = 56 bytes)
                    if len(data) == 56:
                        t_sim, x, y, z, roll, pitch, yaw = struct.unpack('<7d', data)
                        
                        # Store data
                        self.t_data.append(t_sim)
                        self.x_data.append(x)
                        self.y_data.append(y)
                        self.z_data.append(z)
                        self.roll_data.append(roll)
                        self.pitch_data.append(pitch)
                        self.yaw_data.append(yaw)
                        
                        # Print status every 100 cycles
                        if self.counter % 100 == 0:
                            print(f"t={t_sim:.2f}: pos=({x:.2f}, {y:.2f}, {z:.2f}), "
                                  f"ref=({x_ref:.2f}, {y_ref:.2f}, {z_ref:.2f})")
                        
                        # Update plots at reduced rate (25Hz)
                        if self.counter % 4 == 0:  # Update at ~25Hz
                            self.update_plots()
                        
                        self.counter += 1
                        
                except socket.timeout:
                    pass
                
                # Maintain loop rate
                elapsed = time.time() - loop_start
                if elapsed < dt:
                    time.sleep(dt - elapsed)
                    
        except KeyboardInterrupt:
            print("\n  Control loop stopped by user")
            print(" MATLAB is still running with your model")
            print(" You can now work with it in MATLAB or close it manually")
    
    def cleanup(self):
        """Clean up UDP sockets but leave MATLAB running"""
        print(" Cleaning up UDP sockets...")
        if self.sock_tx:
            self.sock_tx.close()
        if self.sock_rx:
            self.sock_rx.close()
        
        # Pause to show final plots
        plt.ioff()
        plt.show(block=False)
        
        print(" Cleanup complete. MATLAB is still running.")
    
    def interactive_mode(self):
        """Enter interactive mode after control loop"""
        print("\n Entering interactive mode. Type 'help' for commands.")
        
        while True:
            cmd = input("\nMATLAB> ").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                print(" Exiting Python. MATLAB remains open.")
                break
                
            elif cmd == 'help':
                print("\nCommands:")
                print("  quit/exit - Exit Python (MATLAB stays open)")
                print("  stop      - Stop simulation")
                print("  start     - Start/resume simulation")
                print("  pause     - Pause simulation")
                print("  status    - Show simulation status")
                print("  who/whos  - List MATLAB workspace variables")
                print("  close     - Close model (but keep MATLAB open)")
                print("  matlab    - Enter MATLAB command directly")
                
            elif cmd == 'stop':
                if self.eng:
                    self.eng.set_param("CONTROL_F2", "SimulationCommand", "stop", nargout=0)
                    print(" Simulation stopped")
                    
            elif cmd == 'start':
                if self.eng:
                    self.eng.set_param("CONTROL_F2", "SimulationCommand", "start", nargout=0)
                    print(" Simulation started")
                    
            elif cmd == 'pause':
                if self.eng:
                    self.eng.set_param("CONTROL_F2", "SimulationCommand", "pause", nargout=0)
                    print(" Simulation paused")
                    
            elif cmd == 'status':
                if self.eng:
                    sim_status = self.eng.get_param("CONTROL_F2", "SimulationStatus")
                    print(f" Simulation status: {sim_status}")
                    
            elif cmd == 'who' or cmd == 'whos':
                if self.eng:
                    if cmd == 'who':
                        result = self.eng.eval("who", nargout=1)
                        print("Workspace variables:", result)
                    else:
                        self.eng.eval("whos", nargout=0)
                        
            elif cmd == 'close':
                if self.eng:
                    self.eng.close_system("CONTROL_F2", nargout=0)
                    print(" Model closed")
                    
            elif cmd == 'matlab':
                matlab_cmd = input("Enter MATLAB command: ")
                try:
                    result = self.eng.eval(matlab_cmd, nargout=1)
                    print(result)
                except Exception as e:
                    print(f"Error: {e}")
                    
            elif cmd.startswith('matlab '):
                # Shortcut for matlab commands
                matlab_cmd = cmd[7:]
                try:
                    result = self.eng.eval(matlab_cmd, nargout=1)
                    print(result)
                except Exception as e:
                    print(f"Error: {e}")
                    
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")

# ===============================
# MAIN EXECUTION
# ===============================

if __name__ == "__main__":
    controller = SimulinkUDPController()
    
    # Step 1: Start MATLAB and open model
    if not controller.start_matlab():
        print(" Failed to start MATLAB")
        sys.exit(1)
    
    # Step 2: Setup UDP
    if not controller.setup_udp():
        print(" Failed to setup UDP")
        sys.exit(1)
    
    # Step 3: Start simulation
    if not controller.start_simulation():
        print(" Failed to start simulation")
        sys.exit(1)
    
    # Step 4: Run control loop
    controller.run_control_loop()
    
    # Step 5: Cleanup UDP (but leave MATLAB running)
    controller.cleanup()
    
    # Step 6: Interactive mode with MATLAB
    controller.interactive_mode()
    
    print("\n Python script ended. MATLAB is still running.")
    print("You can close MATLAB manually or continue working in it.")
import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading

def scan_port(target, port, text_area):
    """Attempts to connect to a specific port on the target."""
    try:
        # Create a socket object using IPv4 and TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a short timeout so we don't wait forever on closed ports
        s.settimeout(0.5)
        
        # Attempt to connect; returns 0 if successful
        result = s.connect_ex((target, port))
        if result == 0:
            text_area.insert(tk.END, f"[+] Port {port} is OPEN\n")
            text_area.see(tk.END) # Auto-scroll
        s.close()
    except Exception as e:
        pass # Ignore errors like connection refused for a cleaner output

def start_scan():
    """Validates input and starts the scanning threads."""
    target = target_entry.get()
    try:
        start_port = int(start_port_entry.get())
        end_port = int(end_port_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Ports must be integers.")
        return

    if not target:
        messagebox.showerror("Error", "Please enter a target IP or hostname.")
        return
        
    if start_port < 1 or end_port > 65535 or start_port > end_port:
         messagebox.showerror("Error", "Invalid port range. Must be 1-65535 and start <= end.")
         return

    # Resolve hostname to IP
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        messagebox.showerror("Error", "Hostname could not be resolved.")
        return

    result_text.delete(1.0, tk.END) # Clear previous results
    result_text.insert(tk.END, f"Starting scan on target: {target_ip}\n")
    result_text.insert(tk.END, f"Scanning ports {start_port} to {end_port}...\n")
    result_text.insert(tk.END, "-"*40 + "\n")

    # Start a separate thread for the scanning loop to keep the GUI responsive
    scan_thread = threading.Thread(target=run_scan_loop, args=(target_ip, start_port, end_port))
    scan_thread.daemon = True # Thread closes when main app closes
    scan_thread.start()

def run_scan_loop(target_ip, start_port, end_port):
    """The main loop that iterates through the port range."""
    scan_button.config(state=tk.DISABLED) # Disable button during scan
    for port in range(start_port, end_port + 1):
        # In a real scanner, you might use a thread pool here.
        # For simplicity and to avoid overwhelming resources, we scan sequentially in this thread.
        scan_port(target_ip, port, result_text)
    
    result_text.insert(tk.END, "-"*40 + "\nScan Complete.\n")
    scan_button.config(state=tk.NORMAL) # Re-enable button

# --- GUI Setup ---
root = tk.Tk()
# Updated title here:
root.title("tkinter Gemini's NMAP 1.X")
root.geometry("450x400")

# Target Input
tk.Label(root, text="Target (IP or Domain):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
target_entry = tk.Entry(root, width=30)
target_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky="w")
target_entry.insert(0, "127.0.0.1") # Default to localhost

# Port Range Inputs
tk.Label(root, text="Start Port:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
start_port_entry = tk.Entry(root, width=10)
start_port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
start_port_entry.insert(0, "1")

tk.Label(root, text="End Port:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
end_port_entry = tk.Entry(root, width=10)
end_port_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
end_port_entry.insert(0, "1024")

# Scan Button
scan_button = tk.Button(root, text="Start Scan", command=start_scan)
scan_button.grid(row=2, column=0, columnspan=4, pady=10)

# Results Area
result_text = scrolledtext.ScrolledText(root, width=50, height=15)
result_text.grid(row=3, column=0, columnspan=4, padx=10, pady=5)

root.mainloop()

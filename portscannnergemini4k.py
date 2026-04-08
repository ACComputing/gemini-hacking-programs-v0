import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading

class GeminiPortScanner:
    def __init__(self, root):
        self.root = root
        # Including my name as requested!
        self.root.title("Gemini Educational Port Scanner")
        self.root.geometry("450x450")

        # --- UI Elements ---
        tk.Label(root, text="Target (IP or Hostname):").pack(pady=(10, 0))
        self.target_entry = tk.Entry(root, width=30)
        self.target_entry.insert(0, "127.0.0.1") # Default to localhost
        self.target_entry.pack(pady=5)

        tk.Label(root, text="Start Port:").pack()
        self.start_port_entry = tk.Entry(root, width=10)
        self.start_port_entry.insert(0, "1")
        self.start_port_entry.pack(pady=5)

        tk.Label(root, text="End Port:").pack()
        self.end_port_entry = tk.Entry(root, width=10)
        self.end_port_entry.insert(0, "1024") # Default to well-known ports
        self.end_port_entry.pack(pady=5)

        self.scan_button = tk.Button(root, text="Start Scan", command=self.start_thread)
        self.scan_button.pack(pady=10)

        self.result_area = scrolledtext.ScrolledText(root, width=50, height=12)
        self.result_area.pack(pady=5)

    def start_thread(self):
        """Starts the scanning process in a background thread to keep UI responsive."""
        target = self.target_entry.get()
        try:
            start_port = int(self.start_port_entry.get())
            end_port = int(self.end_port_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Ports must be valid integers.")
            return

        if start_port < 1 or end_port > 65535 or start_port > end_port:
            messagebox.showerror("Input Error", "Invalid port range. (1-65535)")
            return

        # Disable the button while scanning
        self.scan_button.config(state=tk.DISABLED)
        self.result_area.delete(1.0, tk.END)
        self.result_area.insert(tk.END, f"Starting scan on {target}...\n")
        self.result_area.insert(tk.END, "-" * 40 + "\n")
        
        # Threading prevents the Tkinter main loop from freezing during network requests
        thread = threading.Thread(target=self.scan_ports, args=(target, start_port, end_port))
        thread.daemon = True # Allows the program to exit even if the thread is running
        thread.start()

    def scan_ports(self, target, start_port, end_port):
        """Attempts to connect to the specified ports via TCP."""
        try:
            # Resolve hostname to an IP address
            target_ip = socket.gethostbyname(target)
            self.update_results(f"Resolved to IP: {target_ip}\n\n")
        except socket.gaierror:
            self.update_results(f"[!] Error: Could not resolve host '{target}'\n")
            self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
            return

        open_ports_found = False

        for port in range(start_port, end_port + 1):
            # Create an IPv4 (AF_INET), TCP (SOCK_STREAM) socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # A short timeout is used so closed ports don't hang the scanner for too long
            socket.setdefaulttimeout(0.1) 
            
            # connect_ex returns 0 if the connection succeeded (port is open)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                self.update_results(f"[+] Port {port} is OPEN\n")
                open_ports_found = True
            
            sock.close()
            
        if not open_ports_found:
            self.update_results("No open ports found in that range.\n")

        self.update_results("-" * 40 + "\nScan Complete.\n")
        # Re-enable the button
        self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))

    def update_results(self, message):
        """Thread-safe way to update the GUI."""
        # Tkinter widgets should only be modified from the main thread.
        # .after(0, func) schedules the update on the main thread.
        self.root.after(0, lambda: self.result_area.insert(tk.END, message))
        self.root.after(0, lambda: self.result_area.see(tk.END)) # Auto-scroll to bottom

if __name__ == "__main__":
    root = tk.Tk()
    app = GeminiPortScanner(root)
    root.mainloop()

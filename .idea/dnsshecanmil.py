import os
import subprocess
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox

# DNS settings to be applied
PRIMARY_DNS = "178.22.122.100"
SECONDARY_DNS = "185.51.200.2"
DEFAULT_DNS = "192.168.50.8"

# Backup of the original DNS settings
original_dns = {}


def is_admin():
    """
    Check if the script is running with administrative privileges.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_connected_adapter():
    """
    Get the network adapter that is currently connected to the internet.
    """
    output = subprocess.check_output("netsh interface show interface", shell=True).decode('utf-8')
    lines = output.splitlines()
    for line in lines:
        if "Connected" in line and ("Wi-Fi" in line or "Ethernet" in line):
            return line.split()[-1]
    return None


def get_current_dns(adapter):
    """
    Get the current DNS settings of the given network adapter.
    """
    output = subprocess.check_output(f"netsh interface ip show config name=\"{adapter}\"", shell=True).decode('utf-8')
    lines = output.splitlines()
    dns_list = []
    for line in lines:
        if "DNS Servers" in line or "Statically Configured DNS Servers" in line:
            dns_list.append(line.split()[-1])
    return dns_list


def set_dns(adapter, primary, secondary):
    """
    Set DNS for the given network adapter.
    """
    subprocess.run(f"netsh interface ip set dns name=\"{adapter}\" source=static addr={primary}", shell=True)
    subprocess.run(f"netsh interface ip add dns name=\"{adapter}\" addr={secondary} index=2", shell=True)


def reset_dns(adapter):
    """
    Reset DNS for the given network adapter to the default DNS.
    """
    subprocess.run(f"netsh interface ip set dns name=\"{adapter}\" source=static addr={DEFAULT_DNS}", shell=True)


def toggle_dns():
    global dns_active, original_dns_list
    adapter = get_connected_adapter()
    if not adapter:
        messagebox.showerror("Error", "No network adapter is currently connected.")
        return

    if dns_active:
        # Reset DNS to default DNS
        reset_dns(adapter)
        messagebox.showinfo("DNS Status", "DNS has been reset to the default state (192.168.50.8).")
        toggle_button.config(text="Turn DNS On")
    else:
        # Backup current DNS settings before setting custom DNS
        original_dns_list = get_current_dns(adapter)
        # Set custom DNS
        set_dns(adapter, PRIMARY_DNS, SECONDARY_DNS)
        messagebox.showinfo("DNS Status", "Custom DNS has been set.")
        toggle_button.config(text="Turn DNS Off")

    dns_active = not dns_active


def main():
    if not is_admin():
        # Re-run the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

    global original_dns_list, dns_active, toggle_button

    adapter = get_connected_adapter()
    if not adapter:
        print("No network adapter is currently connected.")
        return

    # Backup current DNS settings
    original_dns_list = get_current_dns(adapter)
    dns_active = False

    # Create GUI
    root = tk.Tk()
    root.title("DNS Switcher")
    root.geometry("300x150")

    toggle_button = tk.Button(root, text="Turn DNS On", command=toggle_dns, height=2, width=15)
    toggle_button.pack(pady=30)

    root.mainloop()


if __name__ == "__main__":
    main()

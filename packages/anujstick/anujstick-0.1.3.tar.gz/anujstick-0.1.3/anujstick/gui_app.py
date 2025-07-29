import tkinter as tk
from anujstick.core import network_attacks, web_exploits, brute_force

def launch_gui():
    window = tk.Tk()
    window.title("AnujStrike - Offensive Toolkit")

    label = tk.Label(window, text="Welcome to AnujStrike GUI!", font=("Arial", 16))
    label.pack(pady=10)

    def run_arp():
        network_attacks.arp_spoof("192.168.1.1", "eth0")

    arp_button = tk.Button(window, text="ARP Spoof Demo", command=run_arp)
    arp_button.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    launch_gui()

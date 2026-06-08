import os
import requests
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

API_KEY = "07fee8ea7efe0641705209a37bd9e23a2988b5b149fd2b5c49f42db26e470daa"
selected_path = ""

# ---------------- VIRUSTOTAL ---------------- #

def is_virus(path):
    url = "https://www.virustotal.com/api/v3/files"

    headers = {
        "accept": "application/json",
        "x-apikey": API_KEY
    }

    try:
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f)}
            upload_response = requests.post(url, files=files, headers=headers)

        if upload_response.status_code != 200:
            return "error"

        ana_id = upload_response.json()["data"]["id"]
        url_check = f"https://www.virustotal.com/api/v3/analyses/{ana_id}"

        status = "queued"
        i = 0

        while status != "completed":
            time.sleep(5)
            response = requests.get(url_check, headers=headers)
            data = response.json()
            status = data["data"]["attributes"]["status"]

            i += 1
            if i >= 30:
                return "unknown"

        malicious = data["data"]["attributes"]["stats"]["malicious"]

        return "virus" if malicious > 0 else "clean"

    except:
        return "error"


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Antivirus Scanner")
root.geometry("800x500")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#2b2b2b",
                foreground="white",
                fieldbackground="#2b2b2b")

style.configure("Treeview.Heading",
                background="#1e1e1e",
                foreground="white")

tree = ttk.Treeview(root)
tree.pack(fill="both", expand=True)

status_label = tk.Label(root, text="Ready", bg="#1e1e1e", fg="white", anchor="w")
status_label.pack(fill="x")

progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress.pack(fill="x")

def choose_folder():
    global selected_path
    selected_path = filedialog.askdirectory()
    status_label.config(text=f"Selected: {selected_path}")

choose_btn = tk.Button(root, text="Choose Folder", command=choose_folder, bg="#555", fg="white")
choose_btn.pack(pady=5)

start_btn = tk.Button(root, text="Start Scan", bg="#3a86ff", fg="white")
start_btn.pack(pady=5)


# ---------------- GLOBALS ---------------- #

node_map = {}
file_list = []
scanned_files = 0


# ---------------- SCAN ---------------- #

def scan_directory(path, parent=""):
    global scanned_files

    try:
        entries = os.listdir(path)
    except:
        return

    for entry in entries:
        full_path = os.path.join(path, entry)

        node = tree.insert(parent, "end", text=entry)
        node_map[full_path] = node

        if os.path.isfile(full_path):

            scanned_files += 1
            status_label.config(text=f"Scanning: {entry}")

            result = is_virus(full_path)

            if result == "virus":
                tree.item(node, text=entry + " ❌ Virus!")
            elif result == "clean":
                tree.item(node, text=entry + " ✅ Clean!")
            elif result == "unknown":
                tree.item(node, text=entry + " ⚠ Unknown!")
            else:
                tree.item(node, text=entry + " ⚠ Error!")

        else:
            scan_directory(full_path, node)


# ---------------- START SCAN ---------------- #

def start_scan():
    global file_list, scanned_files

    scanned_files = 0

    global selected_path

    if not selected_path:
        status_label.config(text="Please choose a folder first")
        return

    path = selected_path

    status_label.config(text="Scanning...")

    # collect files for progress bar
    file_list = []
    for root_dir, dirs, files in os.walk(path):
        for f in files:
            file_list.append(os.path.join(root_dir, f))

    total = len(file_list)
    progress["value"] = 0

    def scan_thread():
        scan_directory(path)
        root.after(0, lambda: status_label.config(text="Scan complete ✔ Done"))
    def progress_thread():
        while True:
            if total > 0:
                progress["value"] = (scanned_files / total) * 100
                root.update_idletasks()

            if scanned_files >= total:
                break

            time.sleep(0.2)

    threading.Thread(target=progress_thread, daemon=True).start()
    threading.Thread(target=scan_thread, daemon=True).start()


start_btn.config(command=start_scan)

root.mainloop()
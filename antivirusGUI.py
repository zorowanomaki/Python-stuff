import os
import requests
import time
import threading
import tkinter as tk
from tkinter import ttk

API_KEY = "07fee8ea7efe0641705209a37bd9e23a2988b5b149fd2b5c49f42db26e470daa"

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
            time.sleep(3)
            response = requests.get(url_check, headers=headers)
            data = response.json()
            status = data["data"]["attributes"]["status"]

            i += 1
            if i >= 10:
                return "unknown"

        malicious = data["data"]["attributes"]["stats"]["malicious"]

        return "virus" if malicious > 0 else "clean"

    except:
        return "error"


# ---------------- GUI SETUP ---------------- #

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
start_btn = tk.Button(root, text="Start Scan", bg="#3a86ff", fg="white")
start_btn.pack(pady=5)
# store mapping: path -> tree node
node_map = {}


# ---------------- SCAN FUNCTION ---------------- #

def scan_directory(path, parent=""):
    try:
        entries = os.listdir(path)
    except:
        return

    for entry in entries:
        full_path = os.path.join(path, entry)

        node = tree.insert(parent, "end", text=entry)
        node_map[full_path] = node

        if os.path.isfile(full_path):
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


# ---------------- THREAD START ---------------- #

def start_scan():
    global file_list, node_map

    path = r"C:\Users\noamb\OneDrive\Documents\Pyton scripts\antivirus"

    status_label.config(text="Scanning...")

    # collect files for progress bar (WITHOUT changing scan logic)
    file_list = []
    for root_dir, dirs, files in os.walk(path):
        for f in files:
            file_list.append(os.path.join(root_dir, f))

    total = len(file_list)
    done = 0

    def wrapped_scan():
        nonlocal done

        scan_directory(path)

        status_label.config(text="Scan complete")

    # wrap original scan but update progress in parallel
    def progress_updater():
        nonlocal done
        while done < total:
            progress["value"] = (done / total) * 100
            root.update_idletasks()
            time.sleep(0.2)

    threading.Thread(target=progress_updater, daemon=True).start()
    threading.Thread(target=wrapped_scan, daemon=True).start()


# threading.Thread(target=start_scan, daemon=True).start()
start_btn.config(command=start_scan)

root.mainloop()
# scan_directory(path=path, prefix="")
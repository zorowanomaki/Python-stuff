import os
import requests
import time
from rich import print
import tkinter as tk

API_KEY = "07fee8ea7efe0641705209a37bd9e23a2988b5b149fd2b5c49f42db26e470daa"

def is_virus(path, prefix=""):
    url = "https://www.virustotal.com/api/v3/files"
   
    headers = {
        "accept": "application/json",
        "x-apikey": API_KEY
    }
    # Upload file
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f)}
        upload_response = requests.post(url, files=files, headers=headers)

    if upload_response.status_code != 200:
        return None
    ana_id = upload_response.json()["data"]["id"]
    url = f"https://www.virustotal.com/api/v3/analyses/{ana_id}"

    response = requests.get(url, headers=headers)
    data = response.json()
    status = data["data"]["attributes"]["status"]
    i = 0
    while status != "completed":
        time.sleep(3)
        response = requests.get(url, headers=headers)
        data = response.json()
        status = data["data"]["attributes"]["status"]
        i+=1
        if i >= 10:
            print (prefix + "Unknown!")
            break
    if i < 10 :
        malicious = data["data"]["attributes"]["stats"]["malicious"]
        print(prefix + "[red]Virus![/red]" if malicious > 0 else prefix + "[green]Clean![/green]")
    


def scan_directory(path, prefix=""):
    entries = os.listdir(path)

    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_last = i == len(entries) - 1

        connector = "└─── " if is_last else "│─── "

        print(prefix + connector + entry)

        if os.path.isfile(full_path):
            is_virus(full_path, prefix + connector)
        else: 
        #if os.path.isfile(full_path) == False:
            new_prefix = prefix + ("     " if is_last else "|    ")
            scan_directory(full_path, new_prefix)

path = r"C:\\Users\\noamb\\OneDrive\\Documents\\Pyton scripts\\antivirus"
scan_directory(path=path, prefix="")
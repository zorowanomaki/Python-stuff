import os


def scan_directory(path, prefix=""):
    entries = os.listdir(path)

    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_last = i == len(entries) - 1

        connector = "└─── " if is_last else "│─── "

        print(prefix + connector + entry)

        if not os.path.isfile(full_path):
            new_prefix = prefix + ("     " if is_last else "|    ")
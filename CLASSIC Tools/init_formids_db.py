import os
import sqlite3
import hashlib

if os.path.exists("../CLASSIC Data/databases/FormIDs.db"):
    os.remove("../CLASSIC Data/databases/FormIDs.db")

conn = sqlite3.connect("../CLASSIC Data/databases/FormIDs.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS Fallout4 
              (id INTEGER PRIMARY KEY AUTOINCREMENT,  
               plugin TEXT, formid TEXT, entry TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS Skyrim
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                 plugin TEXT, formid TEXT, entry TEXT)''')

def insert(line, table="Fallout4"):
    if line:
        if len(line.split(" | ")) >= 3:
            plugin, formid, entry, *extra = line.split(" | ")  # the *extra is for any extraneous data that might be in the line (Python thinks there are more than 3 items in the list for some reason)
            c.execute(f'''INSERT INTO {table} (plugin, formid, entry) 
                      VALUES (?, ?, ?)''', (plugin, formid, entry))

with open("../CLASSIC Data/databases/Fallout4 FID Main.txt", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        insert(line)
if os.path.exists("../CLASSIC Data/databases/Fallout4 FID Mods.txt"):
    with open("../CLASSIC Data/databases/Fallout4 FID Mods.txt", "rb") as f:
        hash = hashlib.sha256(f.read()).hexdigest()
    if not hash == "bb9ebacc7b1cf232becbf00a942105348ced8a25d8e556fa7739845985cb2553":
        with open("../CLASSIC Data/databases/Fallout4 FID Mods.txt", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                insert(line)

if os.path.exists("../CLASSIC Data/databases/Skyrim FID Main.txt"):
    with open("../CLASSIC Data/databases/Skyrim FID Main.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line, "Skyrim")

if os.path.exists("../CLASSIC Data/databases/Skyrim FID Mods.txt"):
    with open("../CLASSIC Data/databases/Skyrim FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line, "Skyrim")

conn.commit()
conn.close()
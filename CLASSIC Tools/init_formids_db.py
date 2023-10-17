import os
import sqlite3
import hashlib

if os.path.exists("../CLASSIC Data/databases/FormIDs.db"):
    os.remove("../CLASSIC Data/databases/FormIDs.db")

def insert(line, table="Fallout4"):
    with sqlite3.connect("../CLASSIC Data/databases/FormIDs.db") as conn:
        c = conn.cursor()
        if line:
            if "|" in line and len(line.split(" | ")) >= 3:
                plugin, formid, entry, *extra = line.split(" | ")  # the *extra is for any extraneous data that might be in the line (Python thinks there are more than 3 items in the list for some reason)
                c.execute(f'''INSERT INTO {table} (plugin, formid, entry) 
                      VALUES (?, ?, ?)''', (plugin, formid, entry))
        conn.commit()

if os.path.exists("../CLASSIC Data/databases/Fallout4 FID Main.txt"):
    with open("../CLASSIC Data/databases/Fallout4 FID Main.txt", encoding="utf-8", errors="ignore") as f:
        print("Inserting Fallout 4 Main FormIDs...")
        for line in f:
            line = line.strip()
            insert(line)
if os.path.exists("../CLASSIC Data/databases/Fallout4 FID Mods.txt"):
    print("Inserting Fallout 4 Mod FormIDs...")
    with open("../CLASSIC Data/databases/Fallout4 FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line)

if os.path.exists("../CLASSIC Data/databases/Skyrim FID Main.txt"):
    print("Inserting Skyrim Main FormIDs...")
    with open("../CLASSIC Data/databases/Skyrim FID Main.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line, "Skyrim")

if os.path.exists("../CLASSIC Data/databases/Skyrim FID Mods.txt"):
    print("Inserting Skyrim Mod FormIDs...")
    with open("../CLASSIC Data/databases/Skyrim FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line, "Skyrim")

if os.path.exists("../CLASSIC Data/databases/Starfield FID Main.txt"):
    print("Inserting Starfield Main FormIDs...")
    with open("../CLASSIC Data/databases/Starfield FID Main.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line, "Starfield")

if os.path.exists("../CLASSIC Data/databases/Starfield FID Mods.txt"):
    print("Inserting Starfield Mod FormIDs...")
    with open("../CLASSIC Data/databases/Starfield FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            insert(line, "Starfield")
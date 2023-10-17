from calendar import c
import os
import sqlite3
import hashlib

if os.path.exists("../CLASSIC Data/databases/FormIDs.db"):
    os.remove("../CLASSIC Data/databases/FormIDs.db")

with sqlite3.connect("../CLASSIC Data/databases/FormIDs.db") as conn:
    c = conn.cursor()
    if os.path.exists("../CLASSIC Data/databases/Fallout4 FID Main.txt"):
        c.execute('''CREATE TABLE IF NOT EXISTS Fallout4 
              (id INTEGER PRIMARY KEY AUTOINCREMENT,  
               plugin TEXT, formid TEXT, entry TEXT)''')
        c.execute("CREATE INDEX IF NOT EXISTS Fallout4_index ON Fallout4(formid, plugin COLLATE nocase);")
    if os.path.exists("../CLASSIC Data/databases/Skyrim FID Main.txt"):
        c.execute('''CREATE TABLE IF NOT EXISTS Skyrim
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                 plugin TEXT, formid TEXT, entry TEXT)''')
        c.execute("CREATE INDEX IF NOT EXISTS Skyrim_index ON Skyrim (formid, plugin COLLATE nocase);")
    if os.path.exists("../CLASSIC Data/databases/Starfield FID Main.txt"):
        c.execute('''CREATE TABLE IF NOT EXISTS Starfield
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                 plugin TEXT, formid TEXT, entry TEXT)''')
        c.execute("CREATE INDEX IF NOT EXISTS Starfield_index ON Starfield (formid, plugin COLLATE nocase);")

def insert(lines, table="Fallout4"):
    with sqlite3.connect("../CLASSIC Data/databases/FormIDs.db") as conn:
        c = conn.cursor()
        if lines:
            for line in lines:
                line = line.strip()
                if "|" in line and len(line.split(" | ")) >= 3:
                    plugin, formid, entry, *extra = line.split(" | ")  # the *extra is for any extraneous data that might be in the line (Python thinks there are more than 3 items in the list for some reason)
                    c.execute(f'''INSERT INTO {table} (plugin, formid, entry) 
                          VALUES (?, ?, ?)''', (plugin, formid, entry))
            conn.commit()

if os.path.exists("../CLASSIC Data/databases/Fallout4 FID Main.txt"):
    with open("../CLASSIC Data/databases/Fallout4 FID Main.txt", encoding="utf-8", errors="ignore") as f:
        print("Inserting Fallout 4 Main FormIDs...")
        insert(f.readlines())
if os.path.exists("../CLASSIC Data/databases/Fallout4 FID Mods.txt"):
    print("Inserting Fallout 4 Mod FormIDs...")
    with open("../CLASSIC Data/databases/Fallout4 FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        insert(f.readlines())

if os.path.exists("../CLASSIC Data/databases/Skyrim FID Main.txt"):
    print("Inserting Skyrim Main FormIDs...")
    with open("../CLASSIC Data/databases/Skyrim FID Main.txt", encoding="utf-8", errors="ignore") as f:
        insert(f.readlines(), "Skyrim")

if os.path.exists("../CLASSIC Data/databases/Skyrim FID Mods.txt"):
    print("Inserting Skyrim Mod FormIDs...")
    with open("../CLASSIC Data/databases/Skyrim FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        insert(f.readlines(), "Skyrim")

if os.path.exists("../CLASSIC Data/databases/Starfield FID Main.txt"):
    print("Inserting Starfield Main FormIDs...")
    with open("../CLASSIC Data/databases/Starfield FID Main.txt", encoding="utf-8", errors="ignore") as f:
        insert(f.readlines(), "Starfield")

if os.path.exists("../CLASSIC Data/databases/Starfield FID Mods.txt"):
    print("Inserting Starfield Mod FormIDs...")
    with open("../CLASSIC Data/databases/Starfield FID Mods.txt", encoding="utf-8", errors="ignore") as f:
        insert(f.readlines(), "Starfield")
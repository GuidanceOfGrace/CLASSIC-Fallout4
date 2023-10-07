import argparse
import os
import sqlite3

argparser = argparse.ArgumentParser()
argparser.add_argument("file", help="The file to add to the database", default="FormID_List.txt")
argparser.add_argument("-t", "--table", help="The table to add the file to", default="Fallout4", nargs=1)
argparser.add_argument("-d", "--db", help="The database to add the file to", default="../CLASSIC Data/databases/FormIDs.db", nargs=1)
argparser.add_argument("-v", "--verbose", help="Prints out the lines as they are added", action="store_true")
args = argparser.parse_args()

if not os.path.exists(args.db):
    raise FileNotFoundError(f"Database {args.db} not found")

conn = sqlite3.connect(args.db)
c = conn.cursor()

with open(args.file, encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        data = line.split(" | ")
        if args.verbose:
            print(f"Adding {line} to {args.table}")
        if " | " in line and len(data) >= 3:
            plugin, formid, entry, *extra = data
            c.execute(f'''INSERT INTO {args.table} (plugin, formid, entry) 
                      VALUES (?, ?, ?)''', (plugin, formid, entry))
conn.commit()
conn.close()
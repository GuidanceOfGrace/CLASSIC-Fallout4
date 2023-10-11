import argparse
import os
import sqlite3

argparser = argparse.ArgumentParser()
argparser.add_argument("file", help="The file to add to the database", default="FormID_List.txt")
argparser.add_argument("-t", "--table", help="The table to add the file to", default="Fallout4", type=str, nargs=1)
argparser.add_argument("-d", "--db", help="The database to add the file to", default="../CLASSIC Data/databases/FormIDs.db", type=str, nargs=1)
argparser.add_argument("-v", "--verbose", help="Prints out the lines as they are added", action="store_true")
args = argparser.parse_args()

if not os.path.exists(args.db):
    raise FileNotFoundError(f"Database {args.db} not found")

conn = sqlite3.connect(args.db)
c = conn.cursor()

with open(args.file, encoding="utf-8", errors="ignore") as f:
    if not args.verbose:
        print(f"Updating database with FormIDs from {args.file} to {args.table}")
    plugins_deleted = []
    plugins_announced = []
    for line in f:
        line = line.strip()
        if " | " in line:
            data = line.split(" | ")
            if len(data) >= 3:
                plugin, formid, entry, *extra = data
                if plugin not in plugins_deleted:
                    print(f"Deleting {plugin}'s FormIDs from {args.table}")
                    c.execute(f"delete from {args.table} where plugin = ?", (plugin,))
                    plugins_deleted.append(plugin)
                if plugin not in plugins_announced and not args.verbose:
                    print(f"Adding {plugin}'s FormIDs to {args.table}")
                    plugins_announced.append(plugin)
                if args.verbose:
                    print(f"Adding {line} to {args.table}")
                c.execute(f'''INSERT INTO {args.table} (plugin, formid, entry) 
                      VALUES (?, ?, ?)''', (plugin, formid, entry))
conn.commit()
print("Optimizing database...")
c.execute("vacuum")
conn.close()

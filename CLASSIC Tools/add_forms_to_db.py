import argparse
import os
import sqlite3
from init_formids_db import insert

argparser = argparse.ArgumentParser()
argparser.add_argument("file", help="The file to add to the database")
argparser.add_argument("--table", help="The table to add the file to", default="Fallout4", nargs=1)
argparser.add_argument("--db", help="The database to add the file to", default="../CLASSIC Data/databases/FormIDs.db", nargs=1)
argparser.add_argument("--verbose", help="Prints out the lines as they are added", action="store_true")
args = argparser.parse_args()

if not os.path.exists(args.db):
    raise FileNotFoundError(f"Database {args.db} not found")

conn = sqlite3.connect(args.db)
c = conn.cursor()

with open(args.file, encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if args.verbose:
            print(f"Adding {line} to {args.table}")
        insert(line, args.table, c)
conn.commit()
conn.close()
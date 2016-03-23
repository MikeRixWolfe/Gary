import os
import sqlite3
import thread

threaddbs={}

def get_db_connection(conn, name=''):
    "returns an sqlite3 connection to a persistent database"

    name = 'bot.db'

    threadid = thread.get_ident()
    if name in threaddbs and threadid in threaddbs[name]:
        return threaddbs[name][threadid]
    filename = os.path.join(bot.persist_dir, name)

    db = sqlite3.connect(filename, timeout=15)
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA busy_timeout = 30000")
        db.commit()
    except:
        pass
    if name in threaddbs:
        threaddbs[name][threadid] = db
    else:
        threaddbs[name] = {threadid: db}
    return db

bot.get_db_connection = get_db_connection

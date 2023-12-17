import hashlib
import sqlite3
import json
import os

salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')

con = sqlite3.connect(db_path)
cur = con.cursor()


### Create tables

### Insert users
###cur.execute(f"""DELETE FROM User WHERE name LIKE '2'""")
###con.commit()

#cur.execute(f"""INSERT INTO Prestar VALUES ('john@gmail.com', '2', '2023-11-23 12:00:57', '')""")
#con.commit()

#cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '2', '2023-11-27 19:32:57', '')""")
#con.commit()
#cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '5', '2023-11-27 19:32:57', '')""")
#con.commit()
#cur.execute(f"""INSERT INTO Prestar VALUES ('juan@gmail.com', '7', '2023-11-27 19:32:57', '')""")
#con.commit()

cur.execute(f"""INSERT INTO Prestar VALUES ('admin@gmail.com', '2', '2023-11-27 19:32:57', '')""")
con.commit()






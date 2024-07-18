import sqlite3 as sql

con = sql.connect('taxi.db')
cur = con.cursor()

cur.execute('''CREATE TABLE users (
            id integer primary key,
            tel text not null,
            count integer
)''')
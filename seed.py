import random
import sqlite3

db = sqlite3.connect('database.db')

db.execute("DELETE FROM Users")
db.execute("DELETE FROM Locations")
db.execute("DELETE FROM Comments")

user_count = 1000
location_count = 10**5
comment_count = 10**6

for i in range(1, user_count + 1):
    db.execute("INSERT INTO Users(username) VALUES (?)",
               ["user" + str(i)])

for i in range(1, location_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("INSERT INTO Locations(name, user_id) VALUES (?, ?)",
               ["location" + str(i), user_id])

for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    location_id = random.randint(1, location_count)
    db.execute("""INSERT INTO Comments (comment, sent_at, user_id, location_id)
                  VALUES (?, datetime('now'), ?, ?)""",
               ["comment" + str(i), user_id, location_id])

db.commit()
db.close()
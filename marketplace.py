import db

def get_locations():
    sql = """SELECT l.id, l.name, l.description, l.image, u.username
             FROM locations l, users u
             WHERE l.user_id = u.id
             GROUP BY l.id
             ORDER BY l.id DESC"""
    return db.query(sql)

def get_location(location_id):
    sql = """SELECT l.id, l.name, l.description, l.user_id, l.image, u.username
             FROM locations l, users u
             WHERE l.user_id = u.id AND l.id = ?"""
    return db.query(sql, [location_id])[0]

def get_comments(location_id):
    sql = """SELECT c.id, c.comment, c.sent_at, c.user_id, u.username
             FROM comments c, users u
             WHERE c.user_id = u.id AND c.location_id = ?
             ORDER BY c.id"""
    try:
        return db.query(sql, [location_id])
    except:
        return []

def get_message(message_id):
    sql = "SELECT id, comment, user_id, location_id FROM messages WHERE id = ?"
    return db.query(sql, [message_id])[0]

def add_location(name, description, user_id, image_data=None):
    sql = "INSERT INTO locations (name, description, user_id, image) VALUES (?, ?, ?, ?)"
    db.execute(sql, [name, description, user_id, image_data])
    location_id = db.last_insert_id()
    # add_message(content, user_id, thread_id)
    return location_id 

def add_comment(content, user_id, location_id):
    sql = """INSERT INTO Comments (comment, user_id, location_id, sent_at) VALUES
             (?, ?, ?, datetime('now'))"""
    db.execute(sql, [content, user_id, location_id])

def update_location(location_id, name, description, image_data=None):
    if image_data:
        sql = "UPDATE Locations SET name = ?, description = ?, image = ? WHERE id = ?"
        db.execute(sql, [name, description, image_data, location_id])
    else:
        sql = "UPDATE Locations SET name = ?, description = ? WHERE id = ?"
        db.execute(sql, [name, description, location_id])

def remove_location(location_id):
    sql = "DELETE FROM locations WHERE id = ?"
    db.execute(sql, [location_id])

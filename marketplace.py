import db

def location_count():
    sql = "SELECT COUNT(*) FROM locations"
    rows = db.query(sql)
    return rows[0][0] if rows else 0

def search_location_count(query):
    sql = """SELECT COUNT(*)
             FROM locations l, users u
             WHERE l.user_id = u.id AND (l.name LIKE ? OR l.description LIKE ?)"""
    like_query = f"%{query}%"
    rows = db.query(sql, [like_query, like_query])
    return rows[0][0] if rows else 0

def get_locations(page, page_size):
    sql = """SELECT l.id, l.name, l.description, l.image, u.username
             FROM locations l, users u
             WHERE l.user_id = u.id
             GROUP BY l.id
             ORDER BY l.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = (page - 1) * page_size 
    return db.query(sql, [limit, offset])

def get_location(location_id):
    sql = """SELECT l.id, l.name, l.description, l.user_id, l.image, u.username
             FROM locations l, users u
             WHERE l.user_id = u.id AND l.id = ?"""
    rows = db.query(sql, [location_id])
    return rows[0] if rows else None

def get_comments(location_id):
    sql = """SELECT c.id, c.comment, c.sent_at, c.user_id, u.username
             FROM comments c, users u
             WHERE c.user_id = u.id AND c.location_id = ? AND c.status = 1
             ORDER BY c.id"""
    try:
        return db.query(sql, [location_id])
    except:
        return []

def get_comment(comment_id):
    sql = "SELECT id, comment, user_id, location_id FROM comments WHERE id = ?"
    rows = db.query(sql, [comment_id])[0]

    if not rows:
        return None
    return rows

def add_location(name, description, user_id, image_data=None):
    sql = "INSERT INTO locations (name, description, user_id, image, created_at) VALUES (?, ?, ?, ?, datetime('now'))"
    db.execute(sql, [name, description, user_id, image_data])
    location_id = db.last_insert_id()
    # add_message(content, user_id, thread_id)
    return location_id 

def add_comment(content, user_id, location_id):
    sql = """INSERT INTO Comments (comment, user_id, location_id, sent_at) VALUES
             (?, ?, ?, datetime('now'))"""
    db.execute(sql, [content, user_id, location_id])

def remove_comment(comment_id):
    sql = "UPDATE Comments SET status = 0 WHERE id = ?"
    db.execute(sql, [comment_id])

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

def update_comment(comment_id, content):
    sql = "UPDATE Comments SET comment = ? WHERE id = ?"
    db.execute(sql, [content, comment_id])

def search_locations(query, page, page_size):
    sql = """SELECT l.id, l.name, l.description, l.image, u.username, l.created_at
             FROM locations l, users u
             WHERE l.user_id = u.id AND (l.name LIKE ? OR l.description LIKE ?)
             GROUP BY l.id
             ORDER BY l.name DESC
             LIMIT ? OFFSET ?"""
    like_query = f"%{query}%"
    limit = page_size
    offset = (page - 1) * page_size 
    return db.query(sql, [like_query, like_query, limit, offset])
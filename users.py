from werkzeug.security import check_password_hash, generate_password_hash
import db

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    print(result)

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id

    return None

def get_user_by_username(username):
    sql = "SELECT id, username, image FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None

def update_profile_image(user_id, image_data):
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image_data, user_id])

def update_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)
    sql = "UPDATE users SET password_hash = ? WHERE id = ?"
    db.execute(sql, [password_hash, user_id])

def update_username(user_id, new_username):
    sql = "UPDATE users SET username = ? WHERE id = ?"
    db.execute(sql, [new_username, user_id])

def update_user_profile(user_id, new_username=None, new_password=None, new_image_data=None):
    if new_username:
        update_username(user_id, new_username)
    if new_password:
        update_password(user_id, new_password)
    if new_image_data:
        update_profile_image(user_id, new_image_data)
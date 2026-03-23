CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
)

CREATE TABLE IF NOT EXISTS Locations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id)
        REFERENCES Users(id)
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY,
    name TEXT
)

CREATE TABLE IF NOT EXISTS LocationCategories (
    location_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (location_id, category_id),
    FOREIGN KEY (location_id)
        REFERENCES Locations(id)
        DELETE ON CASCADE,
    FOREIGN KEY (category_id)
        REFERENCES Categories(id)
        DELETE ON CASCADE,
)

CREATE TABLE IF NOT EXISTS Messages (
    user_id_sender INTEGER,
    user_id_recipient INTEGER,
    message TEXT
    FOREIGN KEY (user_id_sender)
        REFERENCES Users(id),
    FOREIGN KEY (user_id_recipient)
        REFERENCES Users(id),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE IF NOT EXISTS Comments (
    user_id INTEGER,
    comment TEXT,
    location_id INTEGER,
    FOREIGN KEY (user_id)
        REFERENCES Users(id),
    FOREIGN KEY (location_id)
        REFERENCES Locations(id)
        DELETE ON CASCADE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        
CREATE TABLE IF NOT EXISTS Ratings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    rating INTEGER CHECK (rating <= 5 AND rating >= 0),
    location_id INTEGER,
    PRIMARY KEY (user_id, location_id),
    FOREIGN KEY (user_id)
        REFERENCES Users(id),
    FOREIGN KEY (location_id)
        REFERENCES Locations(id)
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS Images (
    id INTEGER PRIMARY KEY,
    location_id INT,
    image BLOB,
    description TEXT,
    FOREIGN KEY (location_id)
        REFERENCES Locations(id)
        ON DELETE CASCADE
)
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS Locations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    user_id INTEGER,
    image BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id)
        REFERENCES Users
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS LocationCategories (
    location_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (location_id, category_id),
    FOREIGN KEY (location_id)
        REFERENCES Locations
        ON DELETE CASCADE,
    FOREIGN KEY (category_id)
        REFERENCES Categories
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Messages (
    user_id_sender INTEGER,
    user_id_recipient INTEGER,
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id_sender)
        REFERENCES Users,
    FOREIGN KEY (user_id_recipient)
        REFERENCES Users
);

CREATE TABLE IF NOT EXISTS Comments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    comment TEXT,
    location_id INTEGER,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1, -- 1: active, 0: deleted
    FOREIGN KEY (user_id)
        REFERENCES Users
    FOREIGN KEY (location_id)
        REFERENCES Locations
        ON DELETE CASCADE
);
        
CREATE TABLE IF NOT EXISTS Ratings (
    user_id INTEGER,
    rating INTEGER CHECK (rating <= 5 AND rating >= 0),
    location_id INTEGER,
    PRIMARY KEY (user_id, location_id),
    FOREIGN KEY (user_id)
        REFERENCES Users
    FOREIGN KEY (location_id)
        REFERENCES Locations
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Images (
    id INTEGER PRIMARY KEY,
    location_id INT,
    image BLOB,
    description TEXT,
    FOREIGN KEY (location_id)
        REFERENCES Locations
        ON DELETE CASCADE
);

CREATE INDEX idx_locations_user_id ON Locations(user_id);
CREATE INDEX idx_comments_location_id ON Comments(location_id);
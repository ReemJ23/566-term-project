-- DriveShare Database Schema

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('owner', 'renter')),
    balance REAL DEFAULT 1000.0,
    q1 TEXT NOT NULL,
    a1 TEXT NOT NULL,
    q2 TEXT NOT NULL,
    a2 TEXT NOT NULL,
    q3 TEXT NOT NULL,
    a3 TEXT NOT NULL
);

CREATE TABLE cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    location TEXT NOT NULL,
    price_per_day REAL NOT NULL,
    available_from TEXT NOT NULL,
    available_to TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY(owner_id) REFERENCES users(id)
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    renter_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'confirmed',
    paid INTEGER DEFAULT 0,
    FOREIGN KEY(car_id) REFERENCES cars(id),
    FOREIGN KEY(renter_id) REFERENCES users(id)
);

CREATE TABLE watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renter_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    target_price REAL,
    notify_when_available INTEGER DEFAULT 1,
    FOREIGN KEY(renter_id) REFERENCES users(id),
    FOREIGN KEY(car_id) REFERENCES cars(id)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

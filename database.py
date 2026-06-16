"""
database.py

SQLite database layer for DriveShare.

This file creates the database tables and provides helper methods for
registration, authentication, car listings, bookings, watchlists, messages,
notifications, and payment balance updates.

The database is intentionally simple and local because this is a standalone
course project.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any


DB_NAME = "driveshare.db"


class DatabaseManager:
    """Handles all SQLite operations for the DriveShare application."""

    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.create_tables()

    def connect(self):
        """Create a database connection."""
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        """Create all required tables if they do not already exist."""
        with self.connect() as conn:
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
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
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS cars (
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
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
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
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    renter_id INTEGER NOT NULL,
                    car_id INTEGER NOT NULL,
                    target_price REAL,
                    notify_when_available INTEGER DEFAULT 1,
                    FOREIGN KEY(renter_id) REFERENCES users(id),
                    FOREIGN KEY(car_id) REFERENCES cars(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(sender_id) REFERENCES users(id),
                    FOREIGN KEY(receiver_id) REFERENCES users(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            conn.commit()

    # ---------------- User Operations ----------------

    def register_user(self, name, email, password, role, q1, a1, q2, a2, q3, a3):
        """Register a new user."""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users
                    (name, email, password, role, q1, a1, q2, a2, q3, a3)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, email, password, role, q1, a1.lower(), q2, a2.lower(), q3, a3.lower()))
                conn.commit()
                return True, "Registration successful."
        except sqlite3.IntegrityError:
            return False, "Email already exists."

    def authenticate(self, email, password) -> Optional[Dict[str, Any]]:
        """Return the user if email and password are correct."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email):
        """Find a user by email."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id):
        """Find a user by ID."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_password(self, user_id, new_password):
        """Update user password after successful recovery."""
        with self.connect() as conn:
            conn.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
            conn.commit()

    # ---------------- Car Operations ----------------

    def add_car(self, car):
        """Add a car listing using a CarListing object."""
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO cars
                (owner_id, model, year, mileage, location, price_per_day, available_from, available_to, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                car.owner_id, car.model, car.year, car.mileage, car.location,
                car.price_per_day, car.available_from, car.available_to, car.description
            ))
            conn.commit()
            return cur.lastrowid

    def get_owner_cars(self, owner_id):
        """Return all cars owned by one owner."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM cars WHERE owner_id=?", (owner_id,))
            return [dict(row) for row in cur.fetchall()]

    def search_cars(self, location, start_date, end_date, max_price=None):
        """
        Search cars by location, date range, and optional maximum price.

        A car is returned only if:
        - It is in the requested location.
        - Its availability range covers the requested rental period.
        - It does not already have an overlapping confirmed booking.
        """
        query = """
            SELECT * FROM cars
            WHERE lower(location) LIKE ?
            AND available_from <= ?
            AND available_to >= ?
        """
        params = [f"%{location.lower()}%", start_date, end_date]

        if max_price:
            query += " AND price_per_day <= ?"
            params.append(float(max_price))

        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query, params)
            cars = [dict(row) for row in cur.fetchall()]

        return [car for car in cars if not self.has_overlapping_booking(car["id"], start_date, end_date)]

    def update_car_price(self, car_id, new_price):
        """Update car price and notify matching watchers."""
        with self.connect() as conn:
            conn.execute("UPDATE cars SET price_per_day=? WHERE id=?", (new_price, car_id))
            conn.commit()

    # ---------------- Booking Operations ----------------

    def has_overlapping_booking(self, car_id, start_date, end_date):
        """
        Check if a car has an existing booking that overlaps with the requested range.

        Overlap rule:
        existing_start <= requested_end AND existing_end >= requested_start
        """
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM bookings
                WHERE car_id=?
                AND status='confirmed'
                AND start_date <= ?
                AND end_date >= ?
            """, (car_id, end_date, start_date))
            return cur.fetchone()[0] > 0

    def create_booking(self, car_id, renter_id, start_date, end_date, total_amount):
        """Create a booking if no overlapping booking exists."""
        if self.has_overlapping_booking(car_id, start_date, end_date):
            return False, "This car is already booked for overlapping dates."

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO bookings
                (car_id, renter_id, start_date, end_date, total_amount)
                VALUES (?, ?, ?, ?, ?)
            """, (car_id, renter_id, start_date, end_date, total_amount))
            conn.commit()
            return True, cur.lastrowid

    def get_booking(self, booking_id):
        """Return booking details."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def mark_booking_paid(self, booking_id):
        """Mark a booking as paid."""
        with self.connect() as conn:
            conn.execute("UPDATE bookings SET paid=1 WHERE id=?", (booking_id,))
            conn.commit()

    # ---------------- Watchlist and Notifications ----------------

    def add_to_watchlist(self, renter_id, car_id, target_price):
        """Add a car to renter watchlist."""
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO watchlists (renter_id, car_id, target_price)
                VALUES (?, ?, ?)
            """, (renter_id, car_id, target_price))
            conn.commit()

    def get_watchers_for_price(self, car_id, new_price):
        """Return renters watching a car whose target price is met."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM watchlists
                WHERE car_id=? AND target_price >= ?
            """, (car_id, new_price))
            return [dict(row) for row in cur.fetchall()]

    def add_notification(self, user_id, message):
        """Create an in-app notification."""
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO notifications (user_id, message)
                VALUES (?, ?)
            """, (user_id, message))
            conn.commit()

    def get_notifications(self, user_id):
        """Get notifications for one user."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM notifications
                WHERE user_id=?
                ORDER BY created_at DESC
            """, (user_id,))
            return [dict(row) for row in cur.fetchall()]

    # ---------------- Messaging ----------------

    def send_message(self, sender_id, receiver_id, content):
        """Send a message between users."""
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO messages (sender_id, receiver_id, content)
                VALUES (?, ?, ?)
            """, (sender_id, receiver_id, content))
            conn.commit()

    def get_messages(self, user_id):
        """Return all messages where the user is sender or receiver."""
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT m.*, s.name AS sender_name, r.name AS receiver_name
                FROM messages m
                JOIN users s ON m.sender_id = s.id
                JOIN users r ON m.receiver_id = r.id
                WHERE sender_id=? OR receiver_id=?
                ORDER BY created_at DESC
            """, (user_id, user_id))
            return [dict(row) for row in cur.fetchall()]

    # ---------------- Payment ----------------

    def transfer_payment(self, renter_id, owner_id, amount):
        """Transfer simulated money from renter to owner."""
        renter = self.get_user_by_id(renter_id)
        if not renter or renter["balance"] < amount:
            return False, "Insufficient renter balance."

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, renter_id))
            cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, owner_id))
            conn.commit()

        return True, "Payment successful."

"""
models.py

This file contains simple data classes used by the DriveShare system.
The classes represent the core entities of the project: User, CarListing,
Booking, Message, and Notification.

The project intentionally keeps the model layer simple so the design patterns
and GUI behavior are easy to understand during the presentation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Represents a DriveShare user."""
    user_id: Optional[int]
    name: str
    email: str
    password: str
    role: str
    balance: float = 1000.0


@dataclass
class CarListing:
    """Represents a car listed by an owner."""
    car_id: Optional[int]
    owner_id: int
    model: str
    year: int
    mileage: int
    location: str
    price_per_day: float
    available_from: str
    available_to: str
    description: str = ""


@dataclass
class Booking:
    """Represents a booking between a renter and a car owner."""
    booking_id: Optional[int]
    car_id: int
    renter_id: int
    start_date: str
    end_date: str
    total_amount: float
    status: str = "confirmed"


@dataclass
class Message:
    """Represents a message sent between two users."""
    message_id: Optional[int]
    sender_id: int
    receiver_id: int
    content: str


@dataclass
class Notification:
    """Represents an in-app notification."""
    notification_id: Optional[int]
    user_id: int
    message: str
    is_read: int = 0

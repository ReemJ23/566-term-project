# DriveShare - Peer-to-Peer Car Rental Platform

DriveShare is a standalone Python/Tkinter application for a peer-to-peer car rental system inspired by Turo. It supports user registration, login, car listing, search, booking, watchlist notifications, messaging, simulated payment, and password recovery.

## How to Run

1. Make sure Python 3.10+ is installed.
2. Open a terminal inside this folder.
3. Run:

```bash
python main.py
```

The application uses SQLite and automatically creates `driveshare.db` on first run.

## Demo Accounts

You can register new accounts from the app. Use role `owner` to list cars and role `renter` to search/book cars.
For testing purposes, the following demo accounts are available:
  - Owner Account
    Email: owner@test.com
    Password: 123
    
  - Renter Account
    Email: renters@test.com
    Password: 123


## Implemented Design Patterns

- Singleton: SessionManager
- Builder: CarListingBuilder
- Observer: Watchlist notification system
- Mediator: AppMediator for GUI navigation and communication
- Proxy: PaymentProxy for secure simulated payment
- Chain of Responsibility: Password recovery security questions

## Repository Contents

- `main.py`: Application entry point and GUI
- `database.py`: SQLite schema and database operations
- `models.py`: Data models
- `patterns/`: Design pattern implementations
- `docs/`: Includes all documents: Presentation, Report, Video, Schema, and UML Diagram

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
- `docs/uml_mermaid.md`: Mermaid UML class diagram
- `docs/database_schema.sql`: SQLite schema
- `docs/report_content.md`: Report draft
- `docs/presentation_content.md`: Slide content and presentation script

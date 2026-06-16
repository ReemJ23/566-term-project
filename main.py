"""
main.py

DriveShare - Peer-to-Peer Car Rental Platform

This is a standalone Tkinter application that demonstrates the required
features and design patterns for the term project.

Implemented features:
- User registration and login
- Three security questions and password recovery
- Owner car listing and price update
- Renter car search
- Booking with overlap prevention
- Watchlist notifications
- Messaging
- Simulated payment
- In-app notifications

Implemented design patterns:
- Singleton: SessionManager
- Builder: CarListingBuilder
- Observer: WatchlistSubject
- Mediator: AppMediator
- Proxy: PaymentProxy
- Chain of Responsibility: PasswordRecoveryChain
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import DatabaseManager
from patterns.singleton_session import SessionManager
from patterns.car_builder import CarListingBuilder
from patterns.observer import WatchlistSubject
from patterns.payment_proxy import PaymentProxy
from patterns.password_recovery_chain import PasswordRecoveryChain
from patterns.mediator import AppMediator


class DriveShareApp(tk.Tk):
    """Main Tkinter application."""

    def __init__(self):
        super().__init__()

        self.title("DriveShare - Peer-to-Peer Car Rental Platform")
        self.geometry("950x650")

        self.db = DatabaseManager()
        self.session = SessionManager()
        self.payment_proxy = PaymentProxy(self.db)
        self.watchlist_subject = WatchlistSubject(self.db)
        self.mediator = AppMediator(self)

        self.selected_car = None
        self.selected_booking_id = None

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for FrameClass in (
            LoginFrame,
            RegisterFrame,
            PasswordRecoveryFrame,
            OwnerDashboardFrame,
            RenterDashboardFrame
        ):
            frame = FrameClass(parent=container, app=self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, frame_name):
        """Raise selected frame."""
        frame = self.frames[frame_name]
        frame.tkraise()

    def refresh_owner_dashboard(self):
        """Refresh owner dashboard after data changes."""
        self.frames["OwnerDashboardFrame"].refresh()

    def refresh_renter_dashboard(self):
        """Refresh renter dashboard after data changes."""
        self.frames["RenterDashboardFrame"].refresh()


class LoginFrame(ttk.Frame):
    """Login screen."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="DriveShare Login", font=("Arial", 22)).pack(pady=25)

        ttk.Label(self, text="Email").pack()
        self.email_entry = ttk.Entry(self, width=40)
        self.email_entry.pack(pady=5)

        ttk.Label(self, text="Password").pack()
        self.password_entry = ttk.Entry(self, width=40, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Register New User", command=self.app.mediator.show_register).pack(pady=5)
        ttk.Button(self, text="Forgot Password", command=self.app.mediator.show_password_recovery).pack(pady=5)

    def login(self):
        """Authenticate user and route based on role."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        user = self.app.db.authenticate(email, password)

        if not user:
            messagebox.showerror("Login Failed", "Invalid email or password.")
            return

        self.app.session.login(user)
        messagebox.showinfo("Success", f"Welcome, {user['name']}!")

        if user["role"] == "owner":
            self.app.mediator.show_owner_dashboard()
        else:
            self.app.mediator.show_renter_dashboard()


class RegisterFrame(ttk.Frame):
    """Registration screen."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Register", font=("Arial", 22)).pack(pady=15)

        form = ttk.Frame(self)
        form.pack()

        self.entries = {}

        labels = [
            "Name", "Email", "Password",
            "Security Question 1", "Answer 1",
            "Security Question 2", "Answer 2",
            "Security Question 3", "Answer 3"
        ]

        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(form, width=50, show="*" if label == "Password" else "")
            entry.grid(row=i, column=1, pady=3)
            self.entries[label] = entry

        ttk.Label(form, text="Role").grid(row=len(labels), column=0, sticky="w")
        self.role_combo = ttk.Combobox(form, values=["owner", "renter"], state="readonly", width=47)
        self.role_combo.set("renter")
        self.role_combo.grid(row=len(labels), column=1, pady=3)

        ttk.Button(self, text="Create Account", command=self.register).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=self.app.mediator.show_login).pack()

    def register(self):
        """Register user and save security questions."""
        name = self.entries["Name"].get().strip()
        email = self.entries["Email"].get().strip()
        password = self.entries["Password"].get().strip()
        role = self.role_combo.get()

        q1 = self.entries["Security Question 1"].get().strip()
        a1 = self.entries["Answer 1"].get().strip()
        q2 = self.entries["Security Question 2"].get().strip()
        a2 = self.entries["Answer 2"].get().strip()
        q3 = self.entries["Security Question 3"].get().strip()
        a3 = self.entries["Answer 3"].get().strip()

        if not all([name, email, password, q1, a1, q2, a2, q3, a3]):
            messagebox.showerror("Error", "All fields are required.")
            return

        success, msg = self.app.db.register_user(name, email, password, role, q1, a1, q2, a2, q3, a3)
        messagebox.showinfo("Registration", msg) if success else messagebox.showerror("Registration", msg)

        if success:
            self.app.mediator.show_login()


class PasswordRecoveryFrame(ttk.Frame):
    """Password recovery screen using Chain of Responsibility."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user_record = None

        ttk.Label(self, text="Password Recovery", font=("Arial", 22)).pack(pady=15)

        ttk.Label(self, text="Email").pack()
        self.email_entry = ttk.Entry(self, width=45)
        self.email_entry.pack(pady=5)

        ttk.Button(self, text="Load Security Questions", command=self.load_questions).pack(pady=10)

        self.questions_label = ttk.Label(self, text="")
        self.questions_label.pack(pady=5)

        self.a1 = ttk.Entry(self, width=45)
        self.a2 = ttk.Entry(self, width=45)
        self.a3 = ttk.Entry(self, width=45)

        self.a1.pack(pady=3)
        self.a2.pack(pady=3)
        self.a3.pack(pady=3)

        ttk.Label(self, text="New Password").pack(pady=5)
        self.new_password = ttk.Entry(self, width=45, show="*")
        self.new_password.pack(pady=3)

        ttk.Button(self, text="Reset Password", command=self.reset_password).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=self.app.mediator.show_login).pack()

    def load_questions(self):
        """Load the user's three security questions."""
        email = self.email_entry.get().strip()
        user = self.app.db.get_user_by_email(email)

        if not user:
            messagebox.showerror("Error", "No user found with this email.")
            return

        self.user_record = user
        self.questions_label.config(
            text=f"Q1: {user['q1']}\nQ2: {user['q2']}\nQ3: {user['q3']}"
        )

    def reset_password(self):
        """Verify answers through chain and update password."""
        if not self.user_record:
            messagebox.showerror("Error", "Load security questions first.")
            return

        chain = PasswordRecoveryChain(self.user_record)

        if not chain.verify(self.a1.get(), self.a2.get(), self.a3.get()):
            messagebox.showerror("Error", "One or more security answers are incorrect.")
            return

        new_password = self.new_password.get().strip()
        if not new_password:
            messagebox.showerror("Error", "New password is required.")
            return

        self.app.db.update_password(self.user_record["id"], new_password)
        messagebox.showinfo("Success", "Password reset successfully.")
        self.app.mediator.show_login()


class OwnerDashboardFrame(ttk.Frame):
    """Owner dashboard for adding cars, managing listings, messages, and notifications."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Owner Dashboard", font=("Arial", 22)).pack(pady=10)

        top = ttk.Frame(self)
        top.pack(fill="x", padx=15)

        ttk.Button(top, text="Logout", command=self.app.mediator.logout).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.add_car_tab = ttk.Frame(notebook)
        self.manage_tab = ttk.Frame(notebook)
        self.messages_tab = ttk.Frame(notebook)
        self.notifications_tab = ttk.Frame(notebook)

        notebook.add(self.add_car_tab, text="Add Car")
        notebook.add(self.manage_tab, text="My Cars")
        notebook.add(self.messages_tab, text="Messages")
        notebook.add(self.notifications_tab, text="Notifications")

        self.build_add_car_tab()
        self.build_manage_tab()
        self.build_messages_tab()
        self.build_notifications_tab()

    def build_add_car_tab(self):
        """Build car listing form."""
        form = ttk.Frame(self.add_car_tab)
        form.pack(pady=10)

        labels = ["Model", "Year", "Mileage", "Location", "Price Per Day", "Available From YYYY-MM-DD", "Available To YYYY-MM-DD", "Description"]
        self.car_entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(form, width=50)
            entry.grid(row=i, column=1, pady=3)
            self.car_entries[label] = entry

        ttk.Button(self.add_car_tab, text="Add Listing", command=self.add_car).pack(pady=10)

    def build_manage_tab(self):
        """Build owner listing management tab."""
        self.cars_tree = ttk.Treeview(self.manage_tab, columns=("id", "model", "location", "price", "dates"), show="headings")
        for col in ("id", "model", "location", "price", "dates"):
            self.cars_tree.heading(col, text=col.title())
        self.cars_tree.pack(fill="both", expand=True, pady=10)

        price_frame = ttk.Frame(self.manage_tab)
        price_frame.pack(pady=5)

        ttk.Label(price_frame, text="New Price").pack(side="left")
        self.new_price_entry = ttk.Entry(price_frame, width=15)
        self.new_price_entry.pack(side="left", padx=5)
        ttk.Button(price_frame, text="Update Selected Car Price", command=self.update_price).pack(side="left")

    def build_messages_tab(self):
        """Build messaging tab."""
        self.owner_messages_text = tk.Text(self.messages_tab, height=18)
        self.owner_messages_text.pack(fill="both", expand=True, pady=5)

        msg_frame = ttk.Frame(self.messages_tab)
        msg_frame.pack(fill="x", pady=5)

        ttk.Label(msg_frame, text="Receiver User ID").pack(side="left")
        self.owner_receiver_entry = ttk.Entry(msg_frame, width=10)
        self.owner_receiver_entry.pack(side="left", padx=5)

        ttk.Label(msg_frame, text="Message").pack(side="left")
        self.owner_message_entry = ttk.Entry(msg_frame, width=50)
        self.owner_message_entry.pack(side="left", padx=5)

        ttk.Button(msg_frame, text="Send", command=self.send_message).pack(side="left")

    def build_notifications_tab(self):
        """Build notifications tab."""
        self.owner_notifications_text = tk.Text(self.notifications_tab, height=22)
        self.owner_notifications_text.pack(fill="both", expand=True)

    def add_car(self):
        """Create car using Builder pattern."""
        user = self.app.session.get_user()

        try:
            builder = CarListingBuilder()
            car = (
                builder
                .set_owner(user["id"])
                .set_basic_info(
                    self.car_entries["Model"].get(),
                    self.car_entries["Year"].get(),
                    self.car_entries["Mileage"].get()
                )
                .set_location(self.car_entries["Location"].get())
                .set_price(self.car_entries["Price Per Day"].get())
                .set_availability(
                    self.car_entries["Available From YYYY-MM-DD"].get(),
                    self.car_entries["Available To YYYY-MM-DD"].get()
                )
                .set_description(self.car_entries["Description"].get())
                .build()
            )

            self.app.db.add_car(car)
            messagebox.showinfo("Success", "Car listing added.")
            self.refresh()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_price(self):
        """Update selected car price and notify watchers using Observer pattern."""
        selected = self.cars_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a car first.")
            return

        car_id = self.cars_tree.item(selected)["values"][0]

        try:
            new_price = float(self.new_price_entry.get())
            self.app.db.update_car_price(car_id, new_price)
            self.app.watchlist_subject.notify_price_drop(car_id, new_price)
            messagebox.showinfo("Success", "Price updated. Matching watchers were notified.")
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid price.")

    def send_message(self):
        """Send a message to another user."""
        user = self.app.session.get_user()

        try:
            receiver_id = int(self.owner_receiver_entry.get())
            content = self.owner_message_entry.get().strip()
            if not content:
                raise ValueError("Message cannot be empty.")
            self.app.db.send_message(user["id"], receiver_id, content)
            messagebox.showinfo("Success", "Message sent.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        """Refresh owner dashboard data."""
        user = self.app.session.get_user()
        if not user:
            return

        for row in self.cars_tree.get_children():
            self.cars_tree.delete(row)

        for car in self.app.db.get_owner_cars(user["id"]):
            self.cars_tree.insert("", "end", values=(
                car["id"],
                car["model"],
                car["location"],
                f"${car['price_per_day']:.2f}",
                f"{car['available_from']} to {car['available_to']}"
            ))

        self.owner_messages_text.delete("1.0", tk.END)
        for msg in self.app.db.get_messages(user["id"]):
            self.owner_messages_text.insert(
                tk.END,
                f"From {msg['sender_name']} to {msg['receiver_name']}: {msg['content']}\n"
            )

        self.owner_notifications_text.delete("1.0", tk.END)
        for note in self.app.db.get_notifications(user["id"]):
            self.owner_notifications_text.insert(tk.END, f"- {note['message']}\n")


class RenterDashboardFrame(ttk.Frame):
    """Renter dashboard for search, booking, watchlist, payment, messages, and notifications."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Renter Dashboard", font=("Arial", 22)).pack(pady=10)

        top = ttk.Frame(self)
        top.pack(fill="x", padx=15)

        ttk.Button(top, text="Logout", command=self.app.mediator.logout).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.search_tab = ttk.Frame(notebook)
        self.payment_tab = ttk.Frame(notebook)
        self.messages_tab = ttk.Frame(notebook)
        self.notifications_tab = ttk.Frame(notebook)

        notebook.add(self.search_tab, text="Search & Book")
        notebook.add(self.payment_tab, text="Payment")
        notebook.add(self.messages_tab, text="Messages")
        notebook.add(self.notifications_tab, text="Notifications")

        self.build_search_tab()
        self.build_payment_tab()
        self.build_messages_tab()
        self.build_notifications_tab()

    def build_search_tab(self):
        """Build search and booking tab."""
        search_frame = ttk.Frame(self.search_tab)
        search_frame.pack(pady=5)

        ttk.Label(search_frame, text="Location").grid(row=0, column=0)
        self.search_location = ttk.Entry(search_frame, width=20)
        self.search_location.grid(row=0, column=1, padx=5)

        ttk.Label(search_frame, text="Start YYYY-MM-DD").grid(row=0, column=2)
        self.search_start = ttk.Entry(search_frame, width=15)
        self.search_start.grid(row=0, column=3, padx=5)

        ttk.Label(search_frame, text="End YYYY-MM-DD").grid(row=0, column=4)
        self.search_end = ttk.Entry(search_frame, width=15)
        self.search_end.grid(row=0, column=5, padx=5)

        ttk.Label(search_frame, text="Max Price").grid(row=1, column=0)
        self.max_price = ttk.Entry(search_frame, width=20)
        self.max_price.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(search_frame, text="Search", command=self.search_cars).grid(row=1, column=2, padx=5)

        self.search_tree = ttk.Treeview(
            self.search_tab,
            columns=("id", "model", "year", "location", "price", "dates"),
            show="headings"
        )

        for col in ("id", "model", "year", "location", "price", "dates"):
            self.search_tree.heading(col, text=col.title())

        self.search_tree.pack(fill="both", expand=True, pady=8)

        actions = ttk.Frame(self.search_tab)
        actions.pack(pady=5)

        ttk.Button(actions, text="Book Selected Car", command=self.book_selected).pack(side="left", padx=5)

        ttk.Label(actions, text="Watch Target Price").pack(side="left", padx=5)
        self.watch_price = ttk.Entry(actions, width=12)
        self.watch_price.pack(side="left")
        ttk.Button(actions, text="Watch Selected Car", command=self.watch_selected).pack(side="left", padx=5)

    def build_payment_tab(self):
        """Build payment tab."""
        ttk.Label(self.payment_tab, text="Selected Booking ID").pack(pady=10)
        self.booking_id_entry = ttk.Entry(self.payment_tab, width=20)
        self.booking_id_entry.pack(pady=5)

        ttk.Button(self.payment_tab, text="Pay for Booking", command=self.pay_booking).pack(pady=10)

        self.payment_status = ttk.Label(self.payment_tab, text="")
        self.payment_status.pack(pady=10)

    def build_messages_tab(self):
        """Build messaging tab."""
        self.renter_messages_text = tk.Text(self.messages_tab, height=18)
        self.renter_messages_text.pack(fill="both", expand=True, pady=5)

        msg_frame = ttk.Frame(self.messages_tab)
        msg_frame.pack(fill="x", pady=5)

        ttk.Label(msg_frame, text="Receiver User ID").pack(side="left")
        self.renter_receiver_entry = ttk.Entry(msg_frame, width=10)
        self.renter_receiver_entry.pack(side="left", padx=5)

        ttk.Label(msg_frame, text="Message").pack(side="left")
        self.renter_message_entry = ttk.Entry(msg_frame, width=50)
        self.renter_message_entry.pack(side="left", padx=5)

        ttk.Button(msg_frame, text="Send", command=self.send_message).pack(side="left")

    def build_notifications_tab(self):
        """Build notifications tab."""
        self.renter_notifications_text = tk.Text(self.notifications_tab, height=22)
        self.renter_notifications_text.pack(fill="both", expand=True)

    def search_cars(self):
        """Search available cars."""
        location = self.search_location.get().strip()
        start = self.search_start.get().strip()
        end = self.search_end.get().strip()
        max_price = self.max_price.get().strip()

        if not location or not start or not end:
            messagebox.showerror("Error", "Location, start date, and end date are required.")
            return

        cars = self.app.db.search_cars(location, start, end, max_price if max_price else None)

        for row in self.search_tree.get_children():
            self.search_tree.delete(row)

        for car in cars:
            self.search_tree.insert("", "end", values=(
                car["id"],
                car["model"],
                car["year"],
                car["location"],
                f"${car['price_per_day']:.2f}",
                f"{car['available_from']} to {car['available_to']}"
            ))

    def calculate_days(self, start, end):
        """Calculate rental days from date strings."""
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
        return max((d2 - d1).days + 1, 1)

    def book_selected(self):
        """Create booking for selected car and prevent overlapping bookings."""
        user = self.app.session.get_user()
        selected = self.search_tree.focus()

        if not selected:
            messagebox.showerror("Error", "Select a car first.")
            return

        values = self.search_tree.item(selected)["values"]
        car_id = int(values[0])
        price_text = str(values[4]).replace("$", "")
        price = float(price_text)
        start = self.search_start.get().strip()
        end = self.search_end.get().strip()

        try:
            days = self.calculate_days(start, end)
            total = days * price
        except ValueError:
            messagebox.showerror("Error", "Dates must use YYYY-MM-DD format.")
            return

        success, result = self.app.db.create_booking(car_id, user["id"], start, end, total)

        if success:
            booking_id = result
            self.booking_id_entry.delete(0, tk.END)
            self.booking_id_entry.insert(0, str(booking_id))
            messagebox.showinfo("Booking Confirmed", f"Booking #{booking_id} created. Total amount: ${total:.2f}")
            self.refresh()
        else:
            messagebox.showerror("Booking Failed", result)

    def watch_selected(self):
        """Add selected car to watchlist."""
        user = self.app.session.get_user()
        selected = self.search_tree.focus()

        if not selected:
            messagebox.showerror("Error", "Select a car first.")
            return

        try:
            car_id = int(self.search_tree.item(selected)["values"][0])
            target_price = float(self.watch_price.get())
            self.app.db.add_to_watchlist(user["id"], car_id, target_price)
            messagebox.showinfo("Watchlist", "Car added to watchlist.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pay_booking(self):
        """Pay using Proxy pattern."""
        try:
            booking_id = int(self.booking_id_entry.get())
            success, message = self.app.payment_proxy.pay_for_booking(booking_id)
            self.payment_status.config(text=message)
            messagebox.showinfo("Payment", message) if success else messagebox.showerror("Payment", message)
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid booking ID.")

    def send_message(self):
        """Send a message to another user."""
        user = self.app.session.get_user()

        try:
            receiver_id = int(self.renter_receiver_entry.get())
            content = self.renter_message_entry.get().strip()
            if not content:
                raise ValueError("Message cannot be empty.")
            self.app.db.send_message(user["id"], receiver_id, content)
            messagebox.showinfo("Success", "Message sent.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        """Refresh messages and notifications."""
        user = self.app.session.get_user()
        if not user:
            return

        self.renter_messages_text.delete("1.0", tk.END)
        for msg in self.app.db.get_messages(user["id"]):
            self.renter_messages_text.insert(
                tk.END,
                f"From {msg['sender_name']} to {msg['receiver_name']}: {msg['content']}\n"
            )

        self.renter_notifications_text.delete("1.0", tk.END)
        for note in self.app.db.get_notifications(user["id"]):
            self.renter_notifications_text.insert(tk.END, f"- {note['message']}\n")


if __name__ == "__main__":
    app = DriveShareApp()
    app.mainloop()

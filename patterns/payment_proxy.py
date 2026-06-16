"""
Proxy Pattern

PaymentProxy controls access to the RealPaymentService.
A real payment gateway is not required for this course project, so the proxy
simulates validation, authorization, balance transfer, and notification.
"""


class RealPaymentService:
    """Simulates the real payment processor."""

    def __init__(self, db):
        self.db = db

    def pay(self, renter_id, owner_id, amount):
        """Transfer balance from renter to owner."""
        return self.db.transfer_payment(renter_id, owner_id, amount)


class PaymentProxy:
    """Secure proxy that validates payment before calling the real service."""

    def __init__(self, db):
        self.db = db
        self.real_service = RealPaymentService(db)

    def pay_for_booking(self, booking_id):
        """
        Simulate payment for a booking.
        The proxy checks booking details before allowing payment.
        """
        booking = self.db.get_booking(booking_id)

        if not booking:
            return False, "Booking not found."

        if booking["paid"] == 1:
            return False, "This booking is already paid."

        car_id = booking["car_id"]
        renter_id = booking["renter_id"]
        amount = booking["total_amount"]

        # Get owner from car record.
        cars = []
        with self.db.connect() as conn:
            conn.row_factory = __import__("sqlite3").Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM cars WHERE id=?", (car_id,))
            car = cur.fetchone()
            if not car:
                return False, "Car not found."
            owner_id = dict(car)["owner_id"]

        success, message = self.real_service.pay(renter_id, owner_id, amount)

        if success:
            self.db.mark_booking_paid(booking_id)
            self.db.add_notification(renter_id, f"Payment of ${amount:.2f} completed for booking #{booking_id}.")
            self.db.add_notification(owner_id, f"You received ${amount:.2f} for booking #{booking_id}.")

        return success, message

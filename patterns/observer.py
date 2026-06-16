"""
Observer Pattern

Renters can watch cars and receive notifications when a car's price becomes
less than or equal to their target price.

The subject is the car price update event.
The observers are renters in the watchlist table.
"""


class WatchlistSubject:
    """Subject that notifies watchers when car conditions change."""

    def __init__(self, db):
        self.db = db

    def notify_price_drop(self, car_id, new_price):
        """
        Notify renters whose target price is met.
        This method is called after an owner updates a car price.
        """
        watchers = self.db.get_watchers_for_price(car_id, new_price)

        for watcher in watchers:
            renter_id = watcher["renter_id"]
            self.db.add_notification(
                renter_id,
                f"Good news! Car #{car_id} price dropped to ${new_price:.2f}, meeting your watchlist target."
            )

"""
Builder Pattern

CarListingBuilder constructs CarListing objects step by step.
This avoids a long constructor call with many optional/variable fields.
"""

from models import CarListing


class CarListingBuilder:
    """Builder for CarListing objects."""

    def __init__(self):
        self.car_id = None
        self.owner_id = None
        self.model = ""
        self.year = 0
        self.mileage = 0
        self.location = ""
        self.price_per_day = 0.0
        self.available_from = ""
        self.available_to = ""
        self.description = ""

    def set_owner(self, owner_id):
        self.owner_id = owner_id
        return self

    def set_basic_info(self, model, year, mileage):
        self.model = model
        self.year = int(year)
        self.mileage = int(mileage)
        return self

    def set_location(self, location):
        self.location = location
        return self

    def set_price(self, price_per_day):
        self.price_per_day = float(price_per_day)
        return self

    def set_availability(self, available_from, available_to):
        self.available_from = available_from
        self.available_to = available_to
        return self

    def set_description(self, description):
        self.description = description
        return self

    def build(self):
        """Validate required fields and return a CarListing object."""
        if not self.owner_id:
            raise ValueError("Owner ID is required.")
        if not self.model:
            raise ValueError("Car model is required.")
        if self.price_per_day <= 0:
            raise ValueError("Price must be greater than zero.")
        if not self.available_from or not self.available_to:
            raise ValueError("Availability dates are required.")

        return CarListing(
            car_id=self.car_id,
            owner_id=self.owner_id,
            model=self.model,
            year=self.year,
            mileage=self.mileage,
            location=self.location,
            price_per_day=self.price_per_day,
            available_from=self.available_from,
            available_to=self.available_to,
            description=self.description
        )

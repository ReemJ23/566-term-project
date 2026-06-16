"""
Singleton Pattern

SessionManager is a Singleton because the application should have only one
active session object at a time. All GUI screens use this same object to know
which user is currently logged in.
"""


class SessionManager:
    """Singleton class that stores the logged-in user."""

    _instance = None

    def __new__(cls):
        """Create only one instance of SessionManager."""
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.current_user = None
        return cls._instance

    def login(self, user):
        """Save the logged-in user."""
        self.current_user = user

    def logout(self):
        """Clear the active user session."""
        self.current_user = None

    def get_user(self):
        """Return the currently logged-in user."""
        return self.current_user

"""
Mediator Pattern

AppMediator centralizes communication between GUI screens.
Instead of screens directly creating or calling each other, they ask the
mediator to navigate or refresh shared data.
"""


class AppMediator:
    """Mediator that controls screen navigation and shared GUI behavior."""

    def __init__(self, app):
        self.app = app

    def show_login(self):
        self.app.show_frame("LoginFrame")

    def show_register(self):
        self.app.show_frame("RegisterFrame")

    def show_password_recovery(self):
        self.app.show_frame("PasswordRecoveryFrame")

    def show_owner_dashboard(self):
        self.app.refresh_owner_dashboard()
        self.app.show_frame("OwnerDashboardFrame")

    def show_renter_dashboard(self):
        self.app.refresh_renter_dashboard()
        self.app.show_frame("RenterDashboardFrame")

    def logout(self):
        self.app.session.logout()
        self.show_login()

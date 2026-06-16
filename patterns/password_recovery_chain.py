"""
Chain of Responsibility Pattern

Password recovery is handled by a chain of three security question handlers.
Each handler checks one question. If the answer is correct, the request moves
to the next handler. If all three handlers pass, the password can be reset.
"""


class SecurityQuestionHandler:
    """Base handler for a security question."""

    def __init__(self, expected_answer):
        self.expected_answer = expected_answer.lower().strip()
        self.next_handler = None

    def set_next(self, handler):
        """Attach the next handler in the chain."""
        self.next_handler = handler
        return handler

    def handle(self, answer):
        """
        Check current answer.
        If correct, continue to next handler.
        """
        if answer.lower().strip() != self.expected_answer:
            return False

        if self.next_handler:
            return self.next_handler.handle_next()

        return True

    def handle_next(self):
        """
        Placeholder used by subclasses/forms.
        In the GUI implementation, each answer is checked directly through
        PasswordRecoveryChain because all answers are collected at once.
        """
        return True


class PasswordRecoveryChain:
    """Builds and executes the three-question recovery chain."""

    def __init__(self, user_record):
        self.user_record = user_record

    def verify(self, answer1, answer2, answer3):
        """
        Verify all three security answers using chain logic.
        """
        h1 = SecurityQuestionHandler(self.user_record["a1"])
        h2 = SecurityQuestionHandler(self.user_record["a2"])
        h3 = SecurityQuestionHandler(self.user_record["a3"])

        h1.set_next(h2).set_next(h3)

        # Since GUI collects all answers at once, process sequentially.
        if answer1.lower().strip() != h1.expected_answer:
            return False
        if answer2.lower().strip() != h2.expected_answer:
            return False
        if answer3.lower().strip() != h3.expected_answer:
            return False

        return True

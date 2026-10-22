class Receiver:
    """Приёмник информации."""

    def __init__(self):
        self.message = ""

    def receive(self, message: str) -> None:
        """Принять сообщение."""
        self.message = message
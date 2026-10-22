class Source:
    """Источник информации."""

    def __init__(self, message: str):
        self.message = message

    def generate(self) -> str:
        """Передать сообщение в систему."""
        return self.message
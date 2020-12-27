from storage import Storage


class Player(Storage):

    def __init__(self, name: str = "Player") -> None:
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return self.name

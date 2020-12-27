from enum import Enum, auto
from typing import List, Optional

from board import Board
from player import Player
from storage import Storage


class Status(Enum):
    WAIT = auto()
    RUN = auto()
    FINISH = auto()


class Match(Storage):
    MAX_PLAYERS: int = 2

    def __init__(self) -> None:
        super().__init__()
        self.players: List[Player] = []
        self.boards: List[Board] = []
        self.status: Status = Status.WAIT
        self.winner: Optional[Player] = None

    def add_player(self, player: Player) -> bool:
        # Check if match is full.
        if len(self.players) >= Match.MAX_PLAYERS:
            return False
        # Check if player already in match.
        if player in self.players:
            return False
        # Add the player to this match.
        self.players.append(player)
        self.boards.append(Board())
        # Now if match is full, start it.
        if len(self.players) == Match.MAX_PLAYERS:
            self.status = Status.RUN
        return True

    def get_player_board(self, player: Player) -> Board:
        return self.boards[self.players.index(player)]

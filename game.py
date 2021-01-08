from enum import Enum, auto
from random import shuffle, randrange
from typing import List, Optional

from basement import Storage


class Block:
    """
    Index is where a block should be to be correct
    and position is where a block is placed at currently.

    If index and position are the same, the block is
    placed currently inside the board.
    """

    def __init__(self, index: int, position: int, is_space: bool):
        self.index = index
        self.position = position
        self.is_space = is_space

    def __str__(self) -> str:
        if self.is_space:
            return "Space Block"
        return f"Block {self.index} at {self.position}"

    @property
    def is_correct(self) -> bool:
        return self.index == self.position

    def export(self) -> dict:
        return {
            "index": self.index,
            "position": self.position,
            "is_space": self.is_space,
        }


class Board(Storage):
    """
    Board contains 9 blocks (1 empty/space).

    Board can be commanded to move any block
    if that block can move at all.
    """

    # Used to know where blocks can move across the board.
    MOVEMENTS: List[List[int]] = [
        # Row 1
        [1, 3],
        [0, 2, 4],
        [1, 5],
        # Row 2
        [0, 4, 6],
        [1, 3, 5, 7],
        [2, 4, 8],
        # Row 3
        [3, 7],
        [4, 6, 8],
        [5, 7],
    ]

    @staticmethod
    def generate_blocks() -> List["Block"]:
        output: List[Block] = []
        for index in range(8):
            output.append(Block(index, 0, False))
        output.append(Block(8, 0, True))
        shuffle(output)
        for block in output:
            block.position = output.index(block)
        return output

    def __init__(self, match: "Match") -> None:
        super().__init__()
        self.blocks: List[Block] = self.generate_blocks()
        self.match = match

    @property
    def is_solved(self) -> bool:
        for block in self.blocks:
            if not block.is_correct:
                return False
        return True

    @property
    def space_block(self) -> "Block":
        for block in self.blocks:
            if block.is_space:
                return block

    def get_block_at_position(self, position: int) -> Optional[Block]:
        for block in self.blocks:
            if block.position == position:
                return block

    def draw(self) -> None:
        output: str = "Board:"
        i: int = 0
        for y in range(3):
            output += "\n"
            for x in range(3):
                block = self.get_block_at_position(i)
                if not block.is_space:
                    output += f"{block.index}-{block.position}\t"
                else:
                    output += f" \t"
                i += 1
        print(output)

    def move_block(self, block: "Block") -> bool:
        # Check if moving a space block.
        if block.is_space:
            return False
        # Store space block.
        space_block: Block = self.space_block
        # Check if space block is in movement of given block.
        if space_block.position not in Board.MOVEMENTS[block.position]:
            return False
        # Swap given block position with space block.
        to_position: int = space_block.position
        space_block.position = block.position
        block.position = to_position
        return True

    def export(self) -> dict:
        blocks: List[dict] = []
        for block in self.blocks:
            blocks.append(block.export())
        return {
            "id": str(self.uid),
            "is_solved": self.is_solved,
            "blocks": blocks,
        }


class Player(Storage):
    """
    Player has a UUID with a name which is not unique.

    Player can be assigned to 1 match at a time. Once
    a player finds a match, they will be kicked out of
    their current match if they are in one.
    """

    def __init__(self, name: str = "Player") -> None:
        super().__init__()
        self.name = name
        self.match: Optional["Match"] = None

    def __str__(self) -> str:
        return self.name

    def export(self, minimal: bool = False) -> dict:
        output: dict = {
            "id": str(self.uid),
            "name": self.name,
        }
        if not minimal:
            output["match"] = str(self.match.uid) if self.match else None
        return output


class Match(Storage):
    """
    Match contains list of players and boards assigned
    to them by their index in the list.

    Only matches with waiting status accept new players,
    once the match has reached maximum number of players
    it starts and will not accept new players anymore.

    Only players who are removed during the waiting status
    are actually removed from the match. Otherwise their
    reference will always be set in the match.
    """

    class Status(Enum):
        # Match is waiting for more players to join.
        WAIT = auto()
        # Match is running, players are playing.
        RUN = auto()
        # Match is over and there's a winner.
        FINISH = auto()

    # Maximum number of players that a match can have.
    MAX_PLAYERS: int = 4

    def __init__(self, max_players: int) -> None:
        super().__init__()
        # List of players in the match.
        self.players: List[Player] = []
        # List of boards for each player.
        self.boards: List[Board] = []
        # Match current status.
        self.status: Match.Status = Match.Status.WAIT
        # Max number of players that can join the match.
        self.max_players: int = max_players
        # Winner player if match is finished.
        self.winner: Optional[Player] = None
        # Board image
        self.boards_image = randrange(6)

    @property
    def is_full(self) -> bool:
        return len(self.players) == self.max_players

    @property
    def active_players(self) -> List[Player]:
        output: List[Player] = []
        for player in self.players:
            if player.match == self:
                output.append(player)
        return output

    def add_player(self, player: Player) -> bool:
        """
        If this match accepts new player currently (determined
        by player count and status) add them and give them a
        board as well.

        :return: Whether player was added.
        """
        # Check if match is not full, already not in or not in waiting status.
        if self.is_full or player in self.players or self.status != Match.Status.WAIT:
            return False
        # Add the player to this match.
        self.players.append(player)
        self.boards.append(Board(self))
        # Set players match
        player.match = self
        # Now if match is full, start it.
        if self.is_full:
            self.status = Match.Status.RUN
        # Player was added, return success.
        return True

    def remove_player(self, player: Player) -> bool:
        """
        Only in waiting status the player is actually completely
        removed and their board is removed as well. In other
        statuses, we need the player and their board to remain.

        When all players leave a match that's running, the match
        status changes to finished.

        :return: Whether player was removed.
        """
        # Validate players match.
        if player.match != self:
            return False
        # Clear player match.
        player.match = None
        # If match is waiting for others to join, let's clear player slot.
        if self.status is Match.Status.WAIT:
            index: int = self.players.index(player)
            self.boards.pop(index)
            self.players.pop(index)
        # If there are no more active players left, finish the match.
        if len(self.active_players) == 0:
            self.status = Match.Status.FINISH
        # Player was removed.
        return True

    def get_player_board(self, player: Player) -> Board:
        return self.boards[self.players.index(player)]

    def get_board_player(self, board: Board) -> Player:
        return self.players[self.boards.index(board)]

    def update_status(self) -> None:
        """
        Check the match and update the status.

        If any board in this match is solved, this match
        is set to finished and the owner of the solved
        board is winner.

        After this match is set as finished, all players
        are removed from the match but their reference
        and boards remain.
        """
        if self.status is Match.Status.RUN:
            for board in self.boards:
                if board.is_solved:
                    self.status = Match.Status.FINISH
                    self.winner = self.get_board_player(board)
                    for player in self.players:
                        self.remove_player(player)
                    break

    def export(self) -> dict:
        boards: List[dict] = []
        players: List[dict] = []
        for board in self.boards:
            boards.append(board.export())
        for player in self.players:
            players.append(player.export(minimal=True))
        return {
            "id": str(self.uid),
            "status": self.status.value,
            "boards": boards,
            "players": players,
            "winner": self.winner.export() if self.winner else None,
            "boards_image": self.boards_image,
        }

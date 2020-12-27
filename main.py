from board import Block, Board
from match import Match
from player import Player

match1 = Match()
player1 = Player("Player 1")
# player2 = Player("Player 2")
match1.add_player(player1)


# match1.add_player(player2)


def start() -> None:
    board: Board = match1.boards[0]
    board.draw()
    move: str = input("Which block do you want to move? ")
    try:
        block: Block = board.get_block_at_position(int(move))
        if block:
            if not board.move_block(block):
                print("That block couldn't be moved.")
        else:
            print("There's no block in given position.")
    except ValueError:
        print("Please enter a number.")
    if board.is_solved:
        print("The puzzle is solved!")
    else:
        start()


if __name__ == "__main__":
    print("Welcome to the very first version of mp8p by Amir Savand.")
    print("Block format is INDEX-POSITION. Enter position number to move the blocks.")
    start()

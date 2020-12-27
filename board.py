from random import shuffle
from typing import List

from storage import Storage


class Block:

    @staticmethod
    def generate() -> List["Block"]:
        output: List[Block] = []
        for index in range(8):
            output.append(Block(index, 0, False))
        output.append(Block(8, 0, True))
        shuffle(output)
        for block in output:
            block.position = output.index(block)
        return output

    @staticmethod
    def get_by_position(blocks: List["Block"], position: int) -> "Block":
        for block in blocks:
            if block.position == position:
                return block

    def __init__(self, index: int, position: int, is_space: bool):
        self.index = index
        self.position = position
        self.is_space = is_space

    def __str__(self) -> str:
        space: str = ""
        if self.is_space:
            space = " (space)"
        return f"Block {self.index} (at {self.position}){space}"


class Board(Storage):
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

    def __init__(self) -> None:
        super().__init__()
        self.blocks: List[Block] = Block.generate()

    @property
    def is_solved(self) -> bool:
        for block in self.blocks:
            if block.index != block.position:
                return False
        return True

    @property
    def space_block(self) -> "Block":
        for block in self.blocks:
            if block.is_space:
                return block

    def get_block_at_position(self, position: int) -> Block:
        return Block.get_by_position(self.blocks, position)

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

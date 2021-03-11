from unittest import TestCase, main

from game import Match, Player, Board


class MatchTestCase(TestCase):

    def test_player_count_and_capacity(self):
        match = Match(max_players=2)
        match.add_player(Player("Player 1"))
        self.assertEqual(len(match.players), 1)
        match.add_player(Player("Player 2"))
        self.assertEqual(len(match.players), 2)

    def test_status(self):
        match = Match(max_players=1)
        self.assertEqual(match.status, Match.Status.WAIT)
        player1 = Player("Player 1")
        match.add_player(player1)
        self.assertEqual(match.status, Match.Status.RUN)
        match.get_player_board(player1).solve()
        match.update_status()
        self.assertEqual(match.status, Match.Status.FINISH)
        self.assertIsNone(player1.match)

    def test_finish_empty_match(self):
        match = Match(max_players=2)
        match.add_player(Player("Player 1"))
        match.add_player(Player("Player 2"))
        self.assertEqual(match.status, Match.Status.RUN)
        match.remove_player(match.players[0])
        self.assertEqual(match.status, Match.Status.RUN)
        match.remove_player(match.players[1])
        self.assertEqual(match.status, Match.Status.FINISH)

    def test_winner_is_board_solver(self):
        match = Match(max_players=2)
        player1 = Player("Player 1")
        player2 = Player("Player 2")
        match.add_player(player1)
        match.add_player(player2)
        match.get_player_board(player1).solve()
        match.update_status()
        self.assertEqual(match.status, Match.Status.FINISH)
        self.assertEqual(match.winner, player1)


class BoardTestCase(TestCase):
    def test_solve(self):
        board = Board()
        self.assertFalse(board.is_solved)
        board.solve()
        self.assertTrue(board.is_solved)

    def test_solvable(self):
        board = Board()
        self.assertTrue(board.is_solvable)
        board.solve()
        board.blocks = [
            board.get_block_at_position(8), board.get_block_at_position(0), board.get_block_at_position(1),
            board.get_block_at_position(3), board.get_block_at_position(4), board.get_block_at_position(2),
            board.get_block_at_position(6), board.get_block_at_position(7), board.get_block_at_position(5),
        ]
        for block in board.blocks:
            block.position = board.blocks.index(block)
        self.assertTrue(board.is_solvable)

    def test_unsolvable(self):
        board = Board()
        board.solve()
        board.blocks = [
            board.get_block_at_position(0), board.get_block_at_position(1), board.get_block_at_position(2),
            board.get_block_at_position(5), board.get_block_at_position(7), board.get_block_at_position(3),
            board.get_block_at_position(4), board.get_block_at_position(6), board.get_block_at_position(8),
        ]
        for block in board.blocks:
            block.position = board.blocks.index(block)
        self.assertFalse(board.is_solvable)


if __name__ == "__main__":
    main()

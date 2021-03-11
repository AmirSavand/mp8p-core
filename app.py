from typing import Optional, cast

from flask import Flask, jsonify, request
from flask_cors import CORS

import version
from basement import get_uuid, ErrorResponse
from game import Player, Match, Board, Block
from websocket import pusher

app: Flask = Flask(__name__)

CORS(app=app)


def get_player_from_request() -> Optional[Player]:
    player_id: str = request.headers.get("player")
    if player_id:
        player = cast(Player, Player.get(get_uuid(player_id)))
        if player:
            return player
    return None


@app.route("/")
def index():
    return jsonify({"version": version.__version__}), 200


@app.route("/register/", methods=["POST"])
def register():
    player: Optional[Player] = get_player_from_request()
    if not player:
        name: str = request.json.get("name")
        if not name:
            return ErrorResponse.message("Please choose a valid display name.")
        player = Player(name=request.json["name"])
    return jsonify(player.export())


@app.route("/find-match/<int:max_players>", methods=["POST"])
def find_match(max_players: int):
    """Find a match for the player to join."""
    # Get the player.
    player: Optional[Player] = get_player_from_request()
    if not player:
        return ErrorResponse.no_player()
    # Match to put player in.
    match: Optional[Match] = None
    # If player is already in a match, kick them out.
    if player.match:
        prev_match: Match = player.match
        prev_match.remove_player(player)
        pusher.trigger(f"match-{prev_match.uid}", "update", prev_match.export())

    # Let's find a match for player to join.
    for item in Match.list(Match):
        item: Match = item
        # Match must be in waiting status with same number of max players.
        if item.status is Match.Status.WAIT and item.max_players == max_players:
            match = item
    # Could not find any match to put player in.
    if not match:
        # Create a new match.
        match = Match(max_players)
    # Add the player to the match.
    match.add_player(player)
    # Trigger update.
    pusher.trigger(f"match-{match.uid}", "update", match.export())
    # Return the match.
    return jsonify(match.export())


@app.route("/match/<uid>/", methods=["GET"])
def match_detail(uid: str):
    player: Optional[Player] = get_player_from_request()
    if not player:
        return ErrorResponse.no_player()
    match: Optional[Match] = Match.get(get_uuid(uid))
    if not match:
        return ErrorResponse.not_found()
    return jsonify(match.export())


@app.route("/board/<uid>/move-block/", methods=["POST"])
def move_board_block(uid: str):
    board: Optional[Board] = Board.get(get_uuid(uid))
    if not board:
        return ErrorResponse.not_found()
    player: Optional[Player] = get_player_from_request()
    if not player:
        return ErrorResponse.no_player()
    player_board: Optional[Board] = player.match.get_player_board(player)
    match: Optional[Match] = player.match
    if not match or player_board.uid != board.uid or match.status is not Match.Status.RUN:
        return ErrorResponse.bad_request()
    block: Optional[Block] = board.get_block_at_position(request.json.get("position"))
    if not board.move_block(block):
        return ErrorResponse.bad_request()
    pusher.trigger(f"board-{board.uid}", "update", board.export())
    match.update_status()
    if match.status is Match.Status.FINISH:
        pusher.trigger(f"match-{match.uid}", "update", match.export())
    return "", 200

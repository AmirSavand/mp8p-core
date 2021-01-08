from os import environ

from pusher import Pusher

pusher = Pusher(
    app_id=environ.get("PUSHER_APP_ID"),
    key=environ.get("PUSHER_KEY"),
    secret=environ.get("PUSHER_SECRET"),
    cluster=environ.get("PUSHER_CLUSTER"),
    ssl=True,
)

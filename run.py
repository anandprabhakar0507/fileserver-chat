

from app import app
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from app.views import socketio


if __name__ == "__main__":
	app.secret_key = 'super secret key'
    # app.config['SESSION_TYPE'] = 'filesystem'
	socketio.run(app,debug=True)
import socketio

sio = socketio.Client(
    logger=True,
    engineio_logger=True,
    reconnection=True,
)

@sio.event
def connect():
    print("connected", sio.sid)

@sio.event
def disconnect():
    print("disconnected")

@sio.on('*')
def catch_all(event, data):
    print(event, data)

sio.connect(
    "http://192.168.1.21",
    socketio_path="/socket.io",
    transports=["polling", "websocket"],
)

sio.wait()


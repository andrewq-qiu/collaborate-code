""""""

import logging
import json
import colorlog
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from document import Document
from transform import DeleteOperation, InsertOperation

# Add Color
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(yellow)s%(message)s',
))

# Restrict logging to this file
logger = colorlog.getLogger('server')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, async_mode=None)

document = Document()


@app.route('/editor/')
def join():
    return render_template('index.html', document=document.get_text(), sync_mode=socket.async_mode)


@socket.on('joined', namespace='/editor')
def joined():
    session_id = request.sid

    document.clients[session_id] = document.get_last_revision_num()
    logger.info(f'User {session_id} has connected to the editor.')

    emit('after-join', session_id, room=session_id)


@socket.on('send operation', namespace='/editor')
def send(raw_data):
    session_id = request.sid

    data = json.loads(raw_data)
    changes = []

    for change in data:
        if change[0] == 'INS':
            operation = InsertOperation(change[1], change[2], session_id)
        elif change[0] == 'DEL':
            operation = DeleteOperation(change[1], session_id)
        else:
            logger.error('A non INS or DEL was given!')
            return

        changes.append(operation)

    if len(changes) == 0 and document.is_on_latest_revision(author=session_id):
        # There are no changes to send
        changes_for_client = []

    elif len(changes) == 0:
        # Implied the document needs to update
        # Add empty changes and get back new changes
        changes_for_client = document.add_changes(changes=changes, author=session_id)
        logger.info(f'User {session_id} updated their document to the latest version.')
    else:
        # Add changes and get back any changes the client needs to append
        changes_for_client = document.add_changes(changes=changes, author=session_id)
        logger.info(f'User {session_id} submitted new changes.')

    emit('call-back', json.dumps(changes_for_client), room=session_id)


@app.route('/api/send')
def send():
    pass


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socket.run(app, debug=True)

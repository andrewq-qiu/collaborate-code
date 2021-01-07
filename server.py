"""Main file for the collaborate-code
project. Run this file to initialize the server.

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
"""

import logging
import json
import colorlog
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from document import Document
from drawing import Drawing
from transform import DeleteOperation, InsertOperation, Position

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
drawing = Drawing()


@app.route('/editor/')
def access() -> str:
    """Called when a user access the editor"""
    return render_template('index.html', document=document.get_text(), sync_mode=socket.async_mode)


@socket.on('joined', namespace='/editor')
def joined() -> None:
    """Receive the emission that a user has loaded and
    joined the editor.

    Emits back to the user confirmation with their
    session id.
    """

    session_id = request.sid

    document.clients[session_id] = document.get_last_revision_num()
    drawing.clients[session_id] = drawing.get_last_revision_num()

    logger.info(f'User {session_id} has connected to the editor.')

    emit('after-join', session_id, json.dumps(list(drawing.get_changes_since_revision_num(-1))), room=session_id)


@socket.on('send-operation', namespace='/editor')
def update(raw_data) -> None:
    """Receive when user sends new operations or wishes
    to update their document to the latest revision.

    Processes new operations (raw_data) and sends back
    any transformed operations the user may be missing.
    """

    session_id = request.sid

    data = json.loads(raw_data)
    changes = []

    for change in data:
        if change[0] == 'INS':
            operation = InsertOperation(Position(change[1][0], change[1][1]), change[2], session_id)
        elif change[0] == 'DEL':
            operation = DeleteOperation(Position(change[1][0], change[1][1]), session_id)
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


@socket.on('send-drawing', namespace='/editor')
def update_drawings(raw_data) -> None:
    session_id = request.sid

    data = json.loads(raw_data)

    changes_for_client = drawing.add_changes(changes=data, author=session_id)

    emit('draw-call-back', json.dumps(changes_for_client), room=session_id)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socket.run(app, debug=True)

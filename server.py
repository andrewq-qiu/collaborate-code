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
from editor import Editor, get_random_string
from transform import DeleteOperation, InsertOperation, Position

# Add Color
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(yellow)s%(message)s',
))

# Restrict logging to this file
logger = colorlog.getLogger('server')
logger.addHandler(handler)
logger.setLevel(logging.INFO)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app, async_mode=None)

# Mapping that maps editor ids to Editors
editors = {}
# Mapping that maps session ids to their editor_ids
clients = {}


@app.route('/editor/', methods=['GET'])
def access() -> str:
    """Called when a user access the editor"""

    editor_id = request.args.get('editor_id')

    if editor_id is None:
        return render_template('editor_home.html', is_error='false')

    elif editor_id in editors:
        editor = editors[editor_id]

        return render_template('editor.html',
                               document=editor.document.get_text(),
                               sync_mode=socket.async_mode)

    else:
        return render_template('editor_home.html', is_error='true')


@app.route('/create/', methods=['GET'])
def create() -> str:
    """Called when a user asks to create a new editor.
    """

    editor_id = get_random_string(5)

    while editor_id in editors:
        editor_id = get_random_string(5)

    editors[editor_id] = Editor()

    logger.info(f'A new editor has been created!')

    return render_template('redirect_to_editor.html', target=editor_id)


@socket.on('joined', namespace='/editor')
def joined(editor_id) -> None:
    """Receive the emission that a user has loaded and
    joined the editor.

    Emits back to the user confirmation with their
    session id.
    """

    session_id = request.sid

    if editor_id not in editors:
        logger.error('A user tried to join with a non-existent editor_id!')
        return

    editor = editors[editor_id]

    # Attach session to this editor
    clients[session_id] = editor_id

    document = editor.document
    drawing = editor.drawing

    document.clients[session_id] = document.get_last_revision_num()
    drawing.clients[session_id] = drawing.get_last_revision_num()

    logger.info(f'Client {session_id} has successfully joined editor {editor_id}.')

    lines = json.dumps(list(drawing.get_changes_since_revision_num(-1)))

    names_and_colors = json.dumps(list(editor.get_clients_state()))

    emit('after-join', (session_id, lines, names_and_colors))


@socket.on('submit-name', namespace='/editor')
def submit_name(name):
    session_id = request.sid

    if session_id not in clients:
        logger.error(f'Client {session_id} invoked submit name but has not properly accessed an editor!')
        return

    editor_id = clients[session_id]
    editor = editors[editor_id]

    if name == '':
        name = 'Anon ' + get_random_string(5)

    color = editor.add_client(session_id, name)
    emit('new-user-joined', (session_id, name, color), broadcast=True)


@socket.on('send-operation', namespace='/editor')
def update(raw_data) -> None:
    """Receive when user sends new operations or wishes
    to update their document to the latest revision.

    Processes new operations (raw_data) and sends back
    any transformed operations the user may be missing.
    """

    session_id = request.sid

    if session_id not in clients:
        logger.error(f'Client {session_id} invoked update but has not properly accessed an editor!')
        return

    editor_id = clients[session_id]
    editor = editors[editor_id]

    document = editor.document

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
        logger.debug(f'User {session_id} updated their document to the latest version.')
    else:
        # Add changes and get back any changes the client needs to append
        changes_for_client = document.add_changes(changes=changes, author=session_id)
        logger.debug(f'User {session_id} submitted new changes.')

    emit('call-back', json.dumps(changes_for_client), room=session_id)


@socket.on('send-drawing', namespace='/editor')
def update_drawings(raw_data) -> None:
    """Receive when user sends new drawn lines
    or wishes to update their drawing to the
    latest state.

    Processes new lines and sends back any new
    lines the user has missed.
    """

    session_id = request.sid

    if session_id not in clients:
        logger.error(
            f'Client {session_id} invoked update_drawings but has not properly accessed an editor!')
        return

    editor_id = clients[session_id]
    editor = editors[editor_id]

    drawing = editor.drawing

    data = json.loads(raw_data)

    changes_for_client = drawing.add_changes(changes=data, author=session_id)

    emit('draw-call-back', json.dumps(changes_for_client), room=session_id)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socket.run(app, debug=False, host='192.168.1.72', port=8080)

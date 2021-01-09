"""Module with the Editor class,
which represents an instance of a
collaborate-code editor.

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
"""

from typing import Dict, Iterator, List, Tuple
import random
import string
import document
import drawing


class Editor:
    """Class representing a collaborate-code editor.

    Instance Attributes:
        - document: the text document of the editor
        - drawing: the drawing of the editor
    """

    document: document.Document
    drawing: drawing.Drawing

    # Private Instance Attribute
    # _clients: a mapping that maps the session id of a client
    #           to their nickname (alias) and colour
    # _colors: a list of the colors available for users
    # _color_index: stores the index of the color chosen
    #               for the next client added
    _clients: Dict[str, Tuple[str, str]]
    _colors: List[str]
    _color_index: int

    def __init__(self):
        """Initialize the editor"""
        # Initialize an empty document
        self.document = document.Document()

        # Initialize an empty drawing
        self.drawing = drawing.Drawing()

        self._clients = {}
        self._colors = ['#AAFF00', '#FFAA00', '#FF00AA', '#AA00FF', '#00AAFF']
        self._color_index = 0

    def get_clients_state(self) -> Iterator[List[str]]:
        """(Generator) Yield an iterator with a list
        in the format [alias, color]
        """

        for session_id in self._clients:
            alias = self._clients[session_id][0]
            color = self._clients[session_id][1]

            yield [alias, color]

    def does_client_exist(self, session_id: str) -> bool:
        """Return whether or not the client exists
        in the editor already.
        """

        return session_id in self._clients

    def add_client(self, session_id: str, alias: str):
        """Add a client to the editor.
        Return the color of the new client

        """
        color = self.get_next_color()

        self._clients[session_id] = (alias, color)

        return color

    def get_next_color(self):
        """Return the next color for a new client"""
        new_color = self._colors[self._color_index]
        self._color_index = (self._color_index + 1) % len(self._colors)

        return new_color


def get_random_string(length: int) -> str:
    """Return a random string of a given length.

    Paramters:
        - length: the length of the string to be generated
    """
    select = string.ascii_lowercase + string.ascii_uppercase + string.digits
    result_str = ''.join(random.choice(select) for _ in range(length))

    return result_str

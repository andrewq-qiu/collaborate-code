"""Module with classes for representing
the text documents of the code editor.

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
"""


import logging
import colorlog
from typing import List, Iterator, Dict
from transform import Operation, xform_multiple

# Add Color
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(yellow)s%(message)s',
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class Revision:
    """Class representing a revision (ordered set of changes)
    that a single user makes.

    Instance Attributes:
        - changes: the list of changes in the revision
        - author: the author's id
        - revision_num: the revision number of the revision in its
                        parent document
    """

    changes: List[Operation]
    author: str
    revision_num: int

    def __init__(self, changes: List[Operation], author: str, revision_num: int) -> None:
        """Initialize the revision."""
        self.changes = changes
        self.author = author
        self.revision_num = revision_num


class Text:
    """Class representing the text of a document."""

    _text: List[List[str]]

    def __init__(self) -> None:
        """Initialize the text"""
        self._text = [[]]

    def get_text(self) -> str:
        """Return the raw string text"""
        return '\n'.join([''.join(row) for row in self._text])

    def apply(self, operation: Operation) -> None:
        """Applies an operation onto the text"""
        identity = operation.get_identity()

        if identity == 'INS':
            if operation.character == '\n':
                left = self._text[operation.position.row][:operation.position.column]
                right = self._text[operation.position.row][operation.position.column:]

                self._text[operation.position.row] = left
                self._text.insert(operation.position.row + 1, right)
            else:
                self._text[operation.position.row].insert(
                    operation.position.column, operation.character)

        elif identity == 'DEL':
            if operation.position.column == -1:
                # Delete row and append to the previous
                row = self._text.pop(operation.position.row)
                self._text[operation.position.row - 1].extend(row)
            else:
                self._text[operation.position.row].pop(operation.position.column)


class Document:
    """Class representing a text document

    Instance Attributes:
        - clients: mapping that maps an author's id
                   to their last reported revision
    """

    clients: Dict[str, int]

    # Private Instance Attributes:
    #   - _revisions: a list of all revisions made in the document
    #   - _text: the Text instance representing the text in the document
    _revisions: List[Revision]
    _text: Text

    def __init__(self) -> None:
        """Initialize the document"""

        self._revisions = []
        # SESSION_ID -> LAST_REVISION
        self.clients = {}
        self._text = Text()

    def get_revision(self, revision_num: int) -> Revision:
        """Return the revision given a revision_num"""
        return self._revisions[revision_num]

    def get_text(self) -> str:
        """Get the raw string text of the document"""
        return self._text.get_text()

    def get_last_revision_num(self) -> int:
        """Return the revision_num of the last revision"""
        return len(self._revisions) - 1

    def is_on_latest_revision(self, author: str) -> bool:
        """Return whether or not the author is on the latest revision
        already.
        """

        return self.get_last_revision_num() == self.clients[author]

    def get_changes_since_revision_num(self, revision_num: int) -> Iterator[Operation]:
        """(Generator) Yield all the changes since a revision_num"""

        rev_range = range(revision_num + 1, self.get_last_revision_num() + 1)

        for i in rev_range:
            rev = self._revisions[i]
            for change in rev.changes:
                yield change

    def add_revision(self, changes: List[Operation], author: str) -> int:
        """Add a new revision to the document given an author
        and a list of changes. Return the new revision_num.
        """

        revision_num = self.get_last_revision_num() + 1
        self._revisions.append(Revision(
            changes=changes, author=author, revision_num=revision_num))
        return revision_num

    def apply_changes(self, changes: List[Operation]) -> None:
        """Apply changes to the text of the document"""

        for change in changes:
            self._text.apply(change)

    def add_changes(self, changes: List[Operation], author: str) -> List[list]:
        """Add changes made by a client and return the changes the
        client needs to make on their end.
        """

        # Last revision submitted by the
        # author is the base of the new
        # revisions
        base = self.clients[author]

        changes_since = list(self.get_changes_since_revision_num(base))

        if len(changes) == 0:
            # The author has made no changes to the document
            # and is instead updating to latest version
            self.clients[author] = self.get_last_revision_num()
            return [change.get_list_structure()
                    for change in changes_since]

        # Transform changes to resend back to client
        # and for the server to re-assume same document state
        changes_for_client, changes_for_server = xform_multiple(changes, changes_since)

        new_revision_num = self.add_revision(changes_for_server, author)
        self.apply_changes(changes_for_server)
        self.clients[author] = new_revision_num

        return [change.get_list_structure()
                for change in changes_for_client]

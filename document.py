
import logging
import colorlog
from typing import List, Iterator
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
    def __init__(self, changes: List[Operation], author: str, revision_num: int):
        self.changes = changes
        self.author = author
        self.revision_num = revision_num


class Text:
    def __init__(self):
        self._text = []

    def get_text(self):
        return ''.join(self._text)

    def apply(self, operation: Operation):
        """Applies an operation onto the text"""
        identity = operation.get_identity()

        if identity == 'INS':
            pos = min(max(operation.position, 0), len(self._text))
            self._text.insert(pos, operation.character)

        elif identity == 'DEL':
            pos = min(max(operation.position, 0), len(self._text) - 1)
            self._text.pop(pos)


class Document:
    def __init__(self):
        self._revisions = []
        # SESSION_ID -> LAST_REVISION
        self.clients = {}
        self._text = Text()

    def get_revision(self, revision: int):
        """"""
        return self._revisions[revision]

    def get_text(self):
        return self._text.get_text()

    def get_last_revision_num(self):
        """"""
        return len(self._revisions) - 1

    def is_on_latest_revision(self, author: str):
        """Return whether or not the author is on the latest revision
        already.
        """

        return self.get_last_revision_num() == self.clients[author]

    def get_changes_since_revision_num(self, revision_num: int) -> Iterator[Operation]:
        """"""

        rev_range = range(revision_num + 1, self.get_last_revision_num() + 1)

        for i in rev_range:
            rev = self._revisions[i]
            for change in rev.changes:
                yield change

    def add_revision(self, changes: List[Operation], author: str):
        revision_num = self.get_last_revision_num() + 1
        self._revisions.append(Revision(
            changes=changes, author=author, revision_num=revision_num))
        return revision_num

    def apply_changes(self, changes: List[Operation]):
        for change in changes:
            self._text.apply(change)

    def add_changes(self, changes: List[Operation], author: str) -> List[list]:
        """"""
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

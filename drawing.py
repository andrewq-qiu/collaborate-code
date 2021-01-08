"""Module with classes for representing
drawn lines and the whiteboard aspect
of the collaborate-code editor.

Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
"""


from typing import Dict, List, Iterator


class Revision:
    """Class representing a revision (ordered set of changes)
    that a single user makes.

    Instance Attributes:
        - changes: the list of changes in the revision
        - author: the author's id
        - revision_num: the revision number of the revision in its
                        parent document
    """

    changes: List[list]
    author: str
    revision_num: int

    def __init__(self, changes: List[list], author: str, revision_num: int) -> None:
        """Initialize the revision."""
        self.changes = changes
        self.author = author
        self.revision_num = revision_num


class Drawing:
    clients: Dict[str, int]

    # Private Instance Attributes:
    #   - _revisions: a list of all revisions made in the document
    #   - _text: the Text instance representing the text in the document
    _revisions: List[Revision]

    def __init__(self):
        """Initialize the Drawing"""

        self._revisions = []
        # SESSION_ID -> LAST_REVISION
        self.clients = {}

    def get_revision(self, revision_num: int) -> Revision:
        """Return the revision given a revision_num"""
        return self._revisions[revision_num]

    def get_last_revision_num(self) -> int:
        """Return the revision_num of the last revision"""
        return len(self._revisions) - 1

    def is_on_latest_revision(self, author: str) -> bool:
        """Return whether or not the author is on the latest revision
        already.
        """

        return self.get_last_revision_num() == self.clients[author]

    def get_changes_since_revision_num(self, revision_num: int) -> Iterator[list]:
        """(Generator) Yield all the changes since a revision_num"""

        rev_range = range(revision_num + 1, self.get_last_revision_num() + 1)

        for i in rev_range:
            rev = self._revisions[i]
            for change in rev.changes:
                yield change

    def add_revision(self, changes: List[list], author: str) -> int:
        """Add a new revision to the document given an author
        and a list of changes. Return the new revision_num.
        """

        revision_num = self.get_last_revision_num() + 1
        self._revisions.append(Revision(
            changes=changes, author=author, revision_num=revision_num))
        return revision_num

    def add_changes(self, changes: List[list], author: str) -> List[list]:
        """Add changes made by a client and return the changes the
        client needs to make on their end.
        """

        base = self.clients[author]
        changes_since = list(self.get_changes_since_revision_num(base))

        new_revision_num = self.add_revision(changes, author)
        self.clients[author] = new_revision_num

        return changes_since


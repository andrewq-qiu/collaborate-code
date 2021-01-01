from dataclasses import dataclass
from typing import List, Tuple


class Operation:
    """Class that represents an
    operation executed on a document that may or may
    not change the document's state.
    """
    author: str

    def get_list_structure(self) -> List[list]:
        """Return the Operation in form of a list
        as to be sent as JSON
        """
        raise NotImplementedError

    def get_identity(self) -> str:
        raise NotImplementedError


@dataclass
class InsertOperation(Operation):
    """A class representing an operation that inserts
    a character a specified position."""

    position: int
    character: str
    author: str

    def get_list_structure(self):
        return ['INS', self.position, self.character, self.author]

    def get_identity(self) -> str:
        return 'INS'

    def __str__(self):
        return f'INS "{self.character}" @ {self.position}'


@dataclass
class DeleteOperation(Operation):
    """A class representing an operation that deletes
    a character at a specified position."""

    position: int
    author: str

    def get_list_structure(self):
        return ['DEL', self.position, self.author]

    def get_identity(self) -> str:
        return 'DEL'

    def __str__(self):
        return f'DEL @ {self.position}'


class IdentityOperation(Operation):
    """A class representing an operation that does nothing
    and preserves the original document state."""

    author: str

    def get_list_structure(self):
        return ['ID', self.author]

    def get_identity(self) -> str:
        return 'ID'

    def __str__(self):
        return 'IDENTITY OPERATOR'


def xform_multiple(op_lefts: List[Operation], op_rights: List[Operation]):
    """"""

    # The operations the left and right side
    # must apply to reach the same state space
    to_apply_left = []
    to_apply_right = []

    current_rights = op_rights

    for i in range(len(op_lefts)):
        next_rights = []

        # The current leftmost operation
        opl = op_lefts[i]

        # The current left operation to be transformed
        current_left = opl

        for j in range(len(current_rights)):
            current_right = current_rights[j]

            # Generate the next_rights
            next_rights.append(xform(current_right, current_left))
            current_left = xform(current_left, current_right)

        to_apply_right.append(current_left)
        current_rights = next_rights

    to_apply_left = current_rights

    return to_apply_left, to_apply_right


def xform(op_1: Operation, op_2: Operation) -> Operation:
    id_1 = op_1.get_identity()
    id_2 = op_2.get_identity()

    # Handle special cases
    if id_1 == 'ID' or id_2 == 'ID':
        return op_1

    options = {
        ('INS', 'INS'): t_ii,
        ('INS', 'DEL'): t_id,
        ('DEL', 'INS'): t_di,
        ('DEL', 'DEL'): t_dd
    }

    return options[(id_1, id_2)](op_1, op_2)


def t_ii(op_1: InsertOperation, op_2: InsertOperation):
    """Return transformed insert op_1 as per
    Operation Transformation with context
    to insert op_2.

    Assume that op_2 is executed first
    """

    # op_2 does not adjust indexes as it is
    # after op_1.
    # break ties by user identifier (no real order)
    if op_1.position < op_2.position or \
            (op_1.position == op_2.position and op_1.author < op_2.author):
        return InsertOperation(op_1.position, op_1.character, op_1.author)
    # op_2 occurs (in index) before op_1 so its execution
    # will push indexes forward by one; adjust accordingly
    else:
        return InsertOperation(op_1.position + 1, op_1.character, op_1.author)


def t_id(op_1: InsertOperation, op_2: DeleteOperation):
    """Return transformed insert op_1 as per
    Operation Transformation with context to
    delete op_2.

    Assume that op_2 is executed first
    """

    # Deletion from op_2 does not affect
    # the indexes for op_1. Make no changes
    if op_1.position <= op_2.position:
        return InsertOperation(op_1.position, op_1.character, op_1.author)
    # Deletion from op_2 pushes op_1 indexes
    # back by one. Adjust accordingly
    else:
        return InsertOperation(op_1.position - 1, op_1.character, op_1.author)


def t_di(op_1: DeleteOperation, op_2: InsertOperation):
    """Return transformed delete op_1 as per
    Operation Transformation with context to
    insert op_2.

    Assume that op_2 is executed first
    """

    # op_2 index position is after
    # op_1 so inserting does not affect
    # op_1 indexes
    if op_1.position < op_2.position:
        return DeleteOperation(op_1.position, op_1.author)
    else:
        return DeleteOperation(op_1.position + 1, op_1.author)


def t_dd(op_1: DeleteOperation, op_2: DeleteOperation):
    """Return transformed delete op_1 as per
    Operation Transformation with context to
    delete op_2.

    Assume that op_2 is executed first
    """

    # Deletion from op_2 does not affect
    # the indexes for op_1. Make no changes
    if op_1.position < op_2.position:
        return DeleteOperation(op_1.position, op_1.author)
    elif op_1.position > op_2.position:
        return DeleteOperation(op_1.position - 1, op_1.author)
    else:
        # They are the same deletion!
        return IdentityOperation()



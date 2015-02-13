from exceptions import Exception

from nouns import *
from date_ops import *
from logic_ops import *
from text_ops import *


class UnknownOperator(Exception):
    def __init__(self, op):
        self.op = op
    def __str__(self):
        return "Unknown operator %s" %(self.op)


def compare(value, op, requirement):
    operator = globals().get(op)
    if operator is None:
        raise UnknownOperator(op)
    return operator(value, requirement)


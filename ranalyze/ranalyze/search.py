"""
Submodule providing database search functionality
"""

import abc
import re

from csv import DictWriter
from enum import Enum
from json import dumps
from sys import stdout
from typing import Tuple, Type
from .config import Config, DictConfigModule
from .database.database import Database
from .database.query import Condition, SelectQuery
from .utils import iso_to_date


KEYWORD_COLUMNS = {"text_content", "title"}

QUOTE_PATTERN = re.compile(r"^([\"'])(?P<text>.*)\1$")


class SearchConfigModule(DictConfigModule):

    _arguments_dict = {
        "database": {
            ("-d", "--database-file"): {
                "help": "SQLite database to search",
                "required": True,
                "type": str
            }
        },
        "search criteria": {
            ("-a", "--after"): {
                "help": "only search posts on or after a specified date"
            },
            ("-b", "--before"): {
                "help": "only search posts on or before a specified date"
            },
            ("-e", "--expression"): {
                "help": ("search using a boolean expression in the"
                         " form:\n[not] \"KEYWORD1\" [and|or] [not]"
                         " \"KEYWORD2\"")
            },
            ("-k", "--keyword"): {
                "action": "append",
                "help": "specify search keywords/phrases"
            },
            ("-s", "--subreddit"): {
                "action": "append",
                "help": "restrict search to specified subreddits"
            }
        },
        "output": {
            ("-c", "--columns"): {
                "help": "space-delimited list of columns to include in results",
                "nargs": "+"
            },
            ("-f", "--format"): {
                "choices": ["json", "csv"],
                "default": "json",
                "help": ("can be used to specify output format, available. "
                         "default is json")
            }
        }
    }

    def get_runner(self):
        return main


from enum import Enum
import abc
import re
from typing import Tuple, Type

QUOTE_PATTERN = re.compile(r"^([\"'])(?P<text>.*)\1$")


class ASTNode(object, metaclass=abc.ABCMeta):
    def __init__(self, data, *children: Tuple['ASTNode']):
        self.children = children
        self.data = data


class OperatorNode(ASTNode, metaclass=abc.ABCMeta):
    """
    Base class for nodes that serve as an operator
    """

    @staticmethod
    @abc.abstractmethod
    def operate(*operands):
        """
        Subclasses should implement this to perform their specific Pythonic
        operational equivalent to one or more operands.
        """
        pass


class InfixNode(OperatorNode, metaclass=abc.ABCMeta):
    """
    Base class for infix operator nodes
    """
    pass


class PrefixNode(OperatorNode, metaclass=abc.ABCMeta):
    """
    Base class for prefix, unary operator nodes.
    """
    pass


class AndNode(InfixNode):
    def __init__(self, *children: Tuple[ASTNode]):
        super().__init__(Operator.AND, *children)

    @staticmethod
    def operate(*operands):
        result = operands[0]
        for operand in operands[1:]:
            result &= operand
        return result


class NotNode(PrefixNode):
    def __init__(self, child: ASTNode):
        super().__init__(Operator.NOT, child)

    @staticmethod
    def operate(*operands):
        return ~operands[0]


class OrNode(InfixNode):
    def __init__(self, *children: Tuple[ASTNode]):
        super().__init__(Operator.OR, *children)

    @staticmethod
    def operate(*operands):
        result = operands[0]
        for operand in operands[1:]:
            result |= operand
        return result


class TextNode(ASTNode):
    def __init__(self, data):
        super().__init__(data)


class Operator(Enum):
    NOT = NotNode
    AND = AndNode
    OR = OrNode

    def __init__(self, node_type: Type[ASTNode]):
        self.node_type = node_type
        self.precedence = [OrNode, AndNode, NotNode].index(node_type)

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.precedence > other.precedence

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.precedence < other.precedence

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.precedence >= other.precedence

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.precedence <= other.precedence


class ExpressionAST(object):
    """
    Syntax tree for representing search logic
    """

    def __init__(self, root_node: ASTNode):
        self.root_node = root_node

    @staticmethod
    def from_expression(expression: str) -> 'ExpressionAST':
        """
        Convert an expression string into a full ExpressionTree.
        Expression strings must be in the following format:
        """
        # TODO: describe syntax

        node_list = []

        # split the expression into a list of tokens and subtrees
        # parenthesized content is isolated and parsed into a subtree first

        paren_start = None
        paren_count = 0
        append_next = False

        for i, c in enumerate(expression):

            if c == "(":
                append_next = False
                if paren_count == 0:
                    paren_start = i
                paren_count += 1

            elif c == ")":
                append_next = False
                paren_count -= 1
                if paren_count == 0:  # process the parenthesized content
                    sub_expression = expression[paren_start + 1:i]
                    sub_tree = ExpressionAST.from_expression(sub_expression)
                    node_list.append(sub_tree.root_node)
                elif paren_count < 0:
                    raise RuntimeError(
                        "Unbalanced right parentheses in search expression")

            elif paren_count > 0:  # don't append what's in the parentheses
                continue

            elif c == " ":  # start a new node next time
                append_next = True

            elif (not node_list
                  or isinstance(node_list[-1], ASTNode)
                  or append_next):  # start a new node with c
                append_next = False
                node_list.append(c)

            else:  # add c to the current node
                node_list[-1] += c

        if paren_count != 0:
            raise RuntimeError(
                "Unbalanced left parentheses in search expression")

        # convert string tokens to operators and TextNodes

        for i, node in enumerate(node_list):

            if isinstance(node, ASTNode):
                continue

            match = QUOTE_PATTERN.match(node)

            if node.upper() in Operator.__members__:
                node_list[i] = Operator[node.upper()].name
            elif match:
                node_list[i] = TextNode(match.group("text"))
            else:
                raise RuntimeError(
                    "Invalid token `{}` in search expression".format(node))

        # parse prefix operators

        output_stack = []

        node_list.reverse()

        while node_list:
            node = node_list.pop()
            if node in Operator.__members__:
                operator = Operator[node]
                if issubclass(operator.node_type, PrefixNode):
                    node = operator.node_type(node_list.pop())
            output_stack.append(node)

        node_list = output_stack

        # Shunting-Yard Algorithm to parse infix operators

        operand_stack = []
        operator_stack = []

        while node_list:
            node = node_list.pop()
            try:
                operator = Operator[node]
                if operator_stack and operator_stack[-1] >= operator:
                    operand_stack.append(operator_stack.pop())
                operator_stack.append(operator)
            except KeyError:
                operand_stack.append(node)

        operator_stack.reverse()
        operand_stack.extend(operator_stack)

        output_stack = []

        operand_stack.reverse()

        while operand_stack:
            node = operand_stack.pop()
            if isinstance(node, Operator):
                if issubclass(node.node_type, InfixNode):
                    node = node.node_type(output_stack.pop(),
                                          output_stack.pop())
                else:
                    node = node.node_type(output_stack.pop())
            output_stack.append(node)

        return ExpressionAST(output_stack.pop())


def multi_column_condition(columns, operand, value) -> Condition:
    """
    Generate an or-joined condition with a single value on multiple columns
    """
    condition = Condition()
    for column in columns:
        condition |= Condition(column, operand, value)
    return condition


def tree_to_condition(tree: ExpressionAST) -> Condition:
    """
    Convert an ExpressionTree to a Condition
    """

    def node_to_condition(node: ASTNode) -> Condition:
        """
        Recursively convert an individual ExpressionNode to a Condition
        """

        if isinstance(node, TextNode):
            value = "%{}%".format(node.data)
            return multi_column_condition(KEYWORD_COLUMNS, "LIKE", value)
        elif isinstance(node, OperatorNode):
            return node.operate(*(node_to_condition(child) for child
                                in node.children))

    return node_to_condition(tree.root_node)


def main():

    config = Config.get_instance()
    database = Database(config["database_file"])

    condition = Condition()  # Empty initial condition

    if config["keyword"]:
        keywords = ["%{}%".format(k) for k in config["keyword"]]
        for word in keywords:
            keyword_condition = multi_column_condition(KEYWORD_COLUMNS,
                                                       "LIKE",
                                                       word)
            condition |= keyword_condition
    elif config["expression"]:
        tree = ExpressionAST.from_expression(config["expression"])
        condition = tree_to_condition(tree)

    if config["subreddit"]:
        subreddit_condition = Condition()
        for sub in config["subreddit"]:
            subreddit_condition |= Condition("subreddit", sub)
        condition &= subreddit_condition

    if config["after"]:
        date = iso_to_date(config["after"])
        condition &= Condition("time_submitted", ">=", date)

    if config["before"]:
        date = iso_to_date(config["before"])
        condition &= Condition("time_submitted", "<=", date)

    columns = ", ".join(config["columns"]) if config["columns"] else "*"

    query = SelectQuery(table=Database.ENTRY_TABLE,
                        distinct=True,
                        where=condition,
                        columns=columns)

    rows = database.execute_query(query, transpose=False)
    entries = [dict(zip(e.keys(), e)) for e in rows]

    if config["format"] == "json":
        print(dumps(entries))
    else:
        if entries:
            keys = config["columns"] if config["columns"] else entries[0].keys()
            writer = DictWriter(stdout, fieldnames=keys)
            writer.writeheader()
            writer.writerows(entries)

"""
Submodule providing database search functionality
"""

import abc
import re
from csv import DictWriter
from json import dumps
from sys import stdout

from ranalyze.ranalyze.query import Condition, SelectQuery
from .config import Config, DictConfigModule
from .database import Database
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


class ASTNode(object, metaclass=abc.ABCMeta):
    def __init__(self, data, left_child: 'ASTNode' = None,
                 right_child: 'ASTNode' = None):
        self.data = data
        self.left_child = left_child
        self.right_child = right_child


class OperatorNode(ASTNode, metaclass=abc.ABCMeta):
    NAME = None

    def __gt__(self, other):
        if not isinstance(other, OperatorNode):
            message = "unorderable types {} > {}".format(self.__class__,
                                                         other.__class__)
            raise TypeError(message)
        return OPERATOR_PRECEDENCE[self.__class__] > OPERATOR_PRECEDENCE[
            other.__class__]

    def __lt__(self, other):
        if not isinstance(other, OperatorNode):
            message = "unorderable types {} < {}".format(self.__class__,
                                                         other.__class__)
            raise TypeError(message)
        return OPERATOR_PRECEDENCE[self.__class__] < OPERATOR_PRECEDENCE[
            other.__class__]

    def __ge__(self, other):
        if not isinstance(other, OperatorNode):
            message = "unorderable types {} >= {}".format(self.__class__,
                                                          other.__class__)
            raise TypeError(message)
        return OPERATOR_PRECEDENCE[self.__class__] >= OPERATOR_PRECEDENCE[
            other.__class__]

    def __le__(self, other):
        if not isinstance(other, OperatorNode):
            message = "unorderable types {} <= {}".format(self.__class__,
                                                          other.__class__)
            raise TypeError(message)
        return OPERATOR_PRECEDENCE[self.__class__] <= OPERATOR_PRECEDENCE[
            other.__class__]


class AndNode(OperatorNode):
    NAME = "AND"

    def __init__(self, left_child: ASTNode = None, right_child: ASTNode = None):
        super().__init__(AndNode.NAME, left_child, right_child)


class OrNode(OperatorNode):
    NAME = "OR"

    def __init__(self, left_child: ASTNode = None, right_child: ASTNode = None):
        super().__init__(OrNode.NAME, left_child, right_child)


class TextNode(ASTNode):
    def __init__(self, data: str):
        super().__init__(data)


class NotNode(ASTNode):
    NAME = "NOT"

    def __init__(self, child: ASTNode = None):
        super().__init__(NotNode.NAME, child)

OPERATOR_PRECEDENCE = {
    AndNode: 2,
    OrNode: 1
    # NOT Tokens are parsed separately, no need to assign precedence
}

OPERATOR_TOKENS = {
    AndNode.NAME: AndNode,
    OrNode.NAME: OrNode,
    NotNode.NAME: NotNode
}

OPERATOR_ACTIONS = {
    AndNode: lambda a, b: a & b,
    OrNode: lambda a, b: a | b,
    NotNode: lambda a, b=None: ~a
}

QUOTES = "'\""


def expression_to_tree(expression: str) -> ASTNode:
    """
    A recursive decent parser using the shunting-yard algorithm to convert
    a well-formed expression string into an abstract syntax tree. The root
    node of this tree is returned.
    """

    # break string into tokens, parsing parenthesized sub-expressions

    tokens = []
    current_token = ""
    in_quotes = False
    paren_count = 0
    paren_start = None

    for i, c in enumerate(expression):

        if c in QUOTES and paren_count == 0:
            if in_quotes:
                tokens.append(current_token + c)
                current_token = ""
                in_quotes = False
            else:
                in_quotes = True
                if current_token:
                    tokens.append(current_token)
                current_token = c
        elif c == " " and not in_quotes and paren_count == 0:
            if current_token:
                tokens.append(current_token)
            current_token = ""
        elif c == "(":
            paren_count += 1
            if paren_count == 1:
                paren_start = i
        elif c == ")":
            paren_count -= 1
            if paren_count == -1:
                raise RuntimeError("Unbalanced right parenthesis in expression")
            if paren_count == 0:
                tokens.append(expression_to_tree(expression[paren_start + 1:i]))
                current_token = ""
        elif paren_count == 0:
            current_token += c

    if current_token:
        tokens.append(current_token)

    if paren_count > 0:
        raise RuntimeError("Unbalanced left parenthesis in expression")

    # convert string tokens to ASTNodes

    nodes = []

    for token in tokens:

        if isinstance(token, ASTNode):
            nodes.append(token)
            continue

        # noinspection PyTypeChecker
        match = QUOTE_PATTERN.match(token)

        if token.upper() in OPERATOR_TOKENS:
            nodes.append(OPERATOR_TOKENS[token.upper()]())
        elif match:
            nodes.append(TextNode(match.group("text")))
        else:
            raise RuntimeError(
                "Invalid token `{}` in expression string".format(token))

    # parse NOT tokens

    infix_nodes = []

    nodes.reverse()

    while nodes:
        node = nodes.pop()
        if isinstance(node, NotNode):
            node.left_child = nodes.pop()
        infix_nodes.append(node)

    # set up nodes as a stack

    infix_nodes.reverse()

    # shunting-yard

    operator_stack = []
    operand_stack = []

    while infix_nodes:
        node = infix_nodes.pop()
        if isinstance(node, OperatorNode):
            if operator_stack and operator_stack[-1] >= node:
                operand_stack.append(operator_stack.pop())
            operator_stack.append(node)
        else:
            operand_stack.append(node)

    operand_stack.extend(operator_stack[::-1])

    operand_stack.reverse()

    output_stack = []

    while operand_stack:
        node = operand_stack.pop()
        if isinstance(node, OperatorNode):
            node.left_child = output_stack.pop()
            node.right_child = output_stack.pop()
        output_stack.append(node)

    return output_stack.pop()


def multi_column_condition(columns, operand, value) -> Condition:
    """
    Generate an or-joined condition with a single value on multiple columns
    """
    condition = Condition()
    for column in columns:
        condition |= Condition(column, operand, value)
    return condition


def tree_to_condition(node: ASTNode) -> Condition:
    """
    Recursively convert an ASTNode to a Condition
    """

    if isinstance(node, TextNode):
        value = "%{}%".format(node.data)
        return multi_column_condition(KEYWORD_COLUMNS, "LIKE", value)
    elif node.__class__ in OPERATOR_ACTIONS:
        action = OPERATOR_ACTIONS[node.__class__]
        a = tree_to_condition(node.left_child)
        b = tree_to_condition(node.right_child) if node.right_child else None
        return action(a, b)
    else:
        raise RuntimeError("Unrecognized node type `{}`".format(node.__class__))


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
        tree = expression_to_tree(config["expression"])
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

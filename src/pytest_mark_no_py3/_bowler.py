import attr
from bowler import SYMBOL
from bowler import TOKEN
from bowler.helpers import find_first
from fissix.fixer_util import Name
from fissix.pytree import Leaf
from fissix.pytree import Node

from . import MARKER as _MARKER

MARKER = "pytest.mark." + _MARKER


@attr.s(frozen=True)
class TestFunc:
    filename = attr.ib(type=str)
    selector = attr.ib(type=str)

    @classmethod
    def from_pytest_results_line(cls, line):
        assert line.startswith(("E", "F"))

        line = line.split(" ", 1)[1]
        filename, selector = line.split("::", 1)

        # Remove parametrization from the test name
        selector = selector.split("[", 1)[0]

        return cls(filename=filename, selector=selector)

    @classmethod
    def from_node(cls, node, filename):
        name_parts = []

        while node:
            possible_name = node.children[1]
            if isinstance(possible_name, Leaf) and possible_name.type == TOKEN.NAME:
                name_parts.append(possible_name.value)

            node = node.parent

        selector = "::".join(reversed(name_parts))
        return cls(filename=filename, selector=selector)


def _get_indent(node):
    """Determine the indentation level of ``node``."""
    indent = None
    while node:
        indent = find_first(node, TOKEN.INDENT)
        if indent is not None:
            indent = indent.value
            break

        node = node.parent

    return indent


def _get_marker(node):
    """
    If ``node`` is already decorated with ``MARKER``, return the
    ``SMYBOL.decorator`` ``Node`` for ``MARKER``.

    Else, return ``None``.
    """
    if node.parent.type == SYMBOL.decorated:
        child = node.parent.children[0]
        if child.type == SYMBOL.decorator:
            decorators = [child]
        elif child.type == SYMBOL.decorators:
            decorators = child.children
        else:
            raise NotImplementedError
        for decorator in decorators:
            name = decorator.children[1]
            assert name.type in {TOKEN.NAME, SYMBOL.dotted_name}

            if str(name) == MARKER:
                return decorator
    return None


def add_marker(node, capture, filename):
    """Add ``MARKER`` to the functions."""
    indent = _get_indent(node)

    decorated = Node(
        SYMBOL.decorated,
        [
            Node(
                SYMBOL.decorator,
                [Leaf(TOKEN.AT, "@"), Name(MARKER), Leaf(TOKEN.NEWLINE, "\n")],
            )
        ],
        prefix=node.prefix,
    )
    node.replace(decorated)
    decorated.append_child(node)

    if indent is not None:
        node.prefix = indent
    else:
        node.prefix = ""


def remove_marker(node, capture, filename):
    """Remove ``MARKER`` from the functions."""
    assert node.parent.type == SYMBOL.decorated

    decorated_node = node.parent

    marker_node = _get_marker(node)

    # Remove the marker from the AST
    marker_node.remove()

    has_other_decorators = any(
        child.type in {SYMBOL.decorator, SYMBOL.decorators}
        for child in decorated_node.children
    )

    if not has_other_decorators:
        # Set the function node's leading whitespace to the same as the marker
        # that was removed
        node.prefix = marker_node.prefix
        # Since there are no other decorators, replace the decorated node with
        # the function node
        decorated_node.replace(node)


def filter_not_already_marked(node, capture, filename):
    """Don't modify tests that are already marked with MARKER."""
    return not _get_marker(node)


def filter_already_marked(node, capture, filename):
    """Only modify tests that are already marked with MARKER."""
    return bool(_get_marker(node))


def filter_failing_tests(results_file):
    """
    Limit to test functions that failed or errored.

    :param file results_file: pytest --result-log file
    """
    testfuncs = {
        TestFunc.from_pytest_results_line(line.strip())
        for line in results_file
        if line.startswith(("F", "E"))
    }

    def inner(node, capture, filename):
        return TestFunc.from_node(node, filename) in testfuncs

    return inner

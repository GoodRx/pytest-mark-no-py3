from textwrap import dedent

from bowler import Query
import pytest

from pytest_mark_no_py3._bowler import add_marker
from pytest_mark_no_py3._bowler import filter_failing_tests
from pytest_mark_no_py3._bowler import filter_not_already_marked
from pytest_mark_no_py3._bowler import TestFunc


class TestTestFunc:
    @pytest.mark.parametrize(
        "line, expected",
        [
            (
                "E tests/some/file/test_foo.py::TestClass::TestNested::test_func[parameter-another]",  # noqa: E501
                TestFunc(
                    "tests/some/file/test_foo.py", "TestClass::TestNested::test_func"
                ),
            ),
            (
                "E tests/another/test_bar.py::test_a_func",
                TestFunc("tests/another/test_bar.py", "test_a_func"),
            ),
            (
                "F test_top.py::TestAnotherClass::test_a_thing",
                TestFunc("test_top.py", "TestAnotherClass::test_a_thing"),
            ),
        ],
    )
    def test_from_pytest_results_line(self, line, expected):
        assert TestFunc.from_pytest_results_line(line) == expected


@pytest.mark.parametrize(
    "src, expected",
    [
        (
            dedent(
                """\
            def top_level():
                pass
            """
            ),
            dedent(
                """\
            @pytest.mark.no_py3
            def top_level():
                pass
            """
            ),
        ),
        (
            dedent(
                """\
            class Outer(object):
                class Inner(object):
                    def method_1(self):
                        pass
                    def method_2(self):
                        pass
            """
            ),
            dedent(
                """\
            class Outer(object):
                class Inner(object):
                    @pytest.mark.no_py3
                    def method_1(self):
                        pass
                    @pytest.mark.no_py3
                    def method_2(self):
                        pass
            """
            ),
        ),
        (
            dedent(
                """\
            @something()
            @pytest.mark.another
            def decorated():
                pass
            """
            ),
            dedent(
                """\
            @something()
            @pytest.mark.another
            @pytest.mark.no_py3
            def decorated():
                pass
            """
            ),
        ),
    ],
)
def test_add_marker(src, expected, tmpdir):
    pyfile = tmpdir.join("t.py")
    pyfile.write(src)

    (
        Query([str(pyfile)])
        .select("funcdef")
        .modify(add_marker)
        .execute(interactive=False, write=True, silent=False, in_process=True)
    )

    modified = pyfile.read()
    assert modified == expected


def filtered_testfuncs(src_file, filter):
    results = []

    def get_testfunc(node, capture, filename):
        results.append(TestFunc.from_node(node, filename))

    (
        Query([str(src_file)])
        .select("funcdef")
        .filter(filter)
        .modify(get_testfunc)
        .execute(interactive=False, write=False, silent=False, in_process=True)
    )

    return results


def test_filter_already_marked(testdir):
    pyfile = testdir.makepyfile(
        dedent(
            """\
        def test_will_be_marked():
            pass

        @pytest.mark.another
        def test_another_that_will_be_marked():
            pass

        @a_decorator()
        @b_decorator
        def test_multiple_decorators_will_be_marked():
            pass

        @pytest.mark.no_py3
        def test_already_marked():
            pass

        @a_decorator()
        @pytest.mark.no_py3
        @another_decorator
        def test_already_marked_many_decorators():
            pass
        """
        )
    )

    expected_testfuncs = [
        TestFunc(str(pyfile), "test_will_be_marked"),
        TestFunc(str(pyfile), "test_another_that_will_be_marked"),
        TestFunc(str(pyfile), "test_multiple_decorators_will_be_marked"),
    ]

    assert filtered_testfuncs(pyfile, filter_not_already_marked) == expected_testfuncs


def test_filter_failing_tests(testdir):
    pyfile = testdir.makepyfile(
        dedent(
            """\
            import pytest

            class TestOuter(object):
                class TestInner(object):
                    @pytest.mark.parametrize("x", [1, 2])
                    def test_passes(self, x):
                        assert True

                    @pytest.mark.parametrize("y", [3, 4])
                    def test_fails(self, y):
                        assert False

            @pytest.fixture
            def bad_fixture():
                assert False

            def test_errors(bad_fixture):
                assert True
        """
        )
    )

    result_log = testdir.tmpdir.join("results.txt")
    testdir.runpytest("--result-log=%s" % result_log)

    expected_testfuncs = [
        TestFunc(pyfile.basename, "TestOuter::TestInner::test_fails"),
        TestFunc(pyfile.basename, "test_errors"),
    ]

    assert (
        filtered_testfuncs(pyfile.basename, filter_failing_tests(result_log.open("r")))
        == expected_testfuncs
    )

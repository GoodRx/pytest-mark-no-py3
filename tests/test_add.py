from textwrap import dedent

import pytest

from pytest_mark_no_py3.add import main


@pytest.mark.parametrize("directory", [True, False])
def test_main_no_results_file(directory, runner, testdir):
    pyfile = testdir.makepyfile(
        dedent(
            """\
        @pytest.mark.no_py3
        def test_already_marked():
            assert False

        def test_will_be_marked():
            assert False
        """
        )
    )
    expected = dedent(
        """\
        @pytest.mark.no_py3
        def test_already_marked():
            assert False

        @pytest.mark.no_py3
        def test_will_be_marked():
            assert False"""
    )

    if directory:
        path = pyfile.dirname
    else:
        path = pyfile
    result = runner.invoke(main, ["--no-interactive", str(path)])
    assert result.exit_code == 0

    assert pyfile.read() == expected


def test_main_with_results_file(runner, testdir):
    pyfile = testdir.makepyfile(
        dedent(
            """\
        import pytest

        @pytest.mark.no_py3
        def test_already_marked():
            assert False

        def test_will_be_marked():
            assert False

        def test_passes():
            assert True
        """
        )
    )
    expected = dedent(
        """\
        import pytest

        @pytest.mark.no_py3
        def test_already_marked():
            assert False

        @pytest.mark.no_py3
        def test_will_be_marked():
            assert False

        def test_passes():
            assert True"""
    )

    result_log = testdir.tmpdir.join("results.txt")
    testdir.runpytest("--result-log=%s" % result_log)

    result = runner.invoke(
        main, ["--no-interactive", "--result-log=%s" % result_log, pyfile.basename]
    )
    assert result.exit_code == 0

    assert pyfile.read() == expected

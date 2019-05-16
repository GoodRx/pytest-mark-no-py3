def test_marker_xfails_on_py3(testdir, mocker):
    """Tests marked with ``no_py3`` are expected to fail on Python 3."""
    mocker.patch("pytest_mark_no_py3.plugin.PY3", new=True)

    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.no_py3
        def test_it():
            assert False
        """
    )

    result = testdir.runpytest()

    assert result.ret == 0
    result.assert_outcomes(xfailed=1)


def test_marker_xfail_strict_on_py3(testdir, mocker):
    """
    Tests marked with ``no_py3`` are expected to fail on Python 3, so passing
    tests will fail pytest.
    """
    mocker.patch("pytest_mark_no_py3.plugin.PY3", new=True)

    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.no_py3
        def test_it():
            assert True
        """
    )

    result = testdir.runpytest()

    assert result.ret == 1
    result.assert_outcomes(failed=1)


def test_marker_passes_on_py2(testdir, mocker):
    """Tests marked with ``no_py3`` are expected to pass on Python 2."""
    mocker.patch("pytest_mark_no_py3.plugin.PY3", new=False)

    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.no_py3
        def test_it():
            assert True
        """
    )

    result = testdir.runpytest()

    assert result.ret == 0
    result.assert_outcomes(passed=1)


def test_marker_no_xfail_on_py2(testdir, mocker):
    """
    Tests marked with ``no_py3`` are expected to pass on Python 2, so failing
    tests will fail pytest.
    """
    mocker.patch("pytest_mark_no_py3.plugin.PY3", new=False)

    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.no_py3
        def test_it():
            assert False
        """
    )

    result = testdir.runpytest()

    assert result.ret == 1
    result.assert_outcomes(failed=1)

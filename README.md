pytest-mark-no-py3
==================

This package provides a pytest plugin and a [Bowler](https://pybowler.io/)
codemod to help migrate tests to Python 3.

Any tests marked with `@pytest.mark.no_py3` will be expected to fail when
running on Python 3 and will fail the test if they pass unexpectedly.

Usage
-----

1. Install this package in your test dependencies.

2. Run your tests on Python 3, savings the results with pytest's `--result-log`
   option, e.g.:

   ```sh
   tox -e py37 -- --result-log=test-results.txt
   ```

3. Install this package with the `bowler` extras in a Python 3 virtualenv:

   ```sh
   pip install pytest_mark_no_py3[bowler]
   ```

4. Apply the marker to all of the tests that failed on Python 3, running from
   the same directory that you ran the tests from:

   ```sh
   python -m pytest_mark_no_py3.add --result-log=path/to/result-log.txt path/to/your/tests
   ```

   If you're feeling confident, you can also use the `--no-interactive` option
   to apply the codemod without prompting to accept changes.

Running tests
-------------

Run `tox`.

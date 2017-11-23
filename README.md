Documentation build, testing and linting for the `master` branch.

[![Documentation Status][docs_badge]][docs] [![Build Status][build_badge]][build] [![Maintainability][maintainability_badge]][maintainability] [![Test Coverage][test_coverage_badge]][test_coverage]

Logger Helper
=============

Logger Helper provides a simple way to gather verbose logs within your
application. Set up your logging using the standard `logging` library and
decorate your classes, methods and functions (or even do it at the module
level with the `mod` method) to get detailed logs of what your application is
doing:

```
Calling __main__.Test.add(a = 1, b = 2, c = 3)
Returned 6 from __main__.Test.add
Calling __main__.Test.subtract(a = 3, b = 2, c = 2)
Returned -1 from __main__.Test.subtract
Calling __main__.Test.divide_by_zero(a = 10)
Exception ZeroDivisionError occurred, "division by zero"
```

Installation
------------

To install the Logger Helper package, ensure you have pip installed using your
distributions package manager and then run the following command:

```bash
pip install logger-helper
```

Basic Usage
-----------

You can start using the `LoggerHelper` right away.

```python
import logging
from logger_helper import LoggerHelper

# Perform your standard logging setup here

log = LoggerHelper(logging.getLogger(__name__), logging.DEBUG)

# DONE! Start decorating your modules, classes and functions:

@log
class MyClass:
    def method_1(self):
        pass

    def method_2(self):
        pass

@log
def function():
    pass
```

For more information, be sure to read [the documentation][docs]. If you clone
this repository and install [invoke][invoke], you can serve
the documentation locally with `invoke serve-docs`.


[docs]: http://logger-helper.readthedocs.io/en/latest/
[invoke]: http://www.pyinvoke.org
[build]: https://travis-ci.org/vimist/logger-helper
[maintainability]: https://codeclimate.com/github/vimist/logger-helper/maintainability
[test_coverage]: https://codeclimate.com/github/vimist/logger-helper/test_coverage

[docs_badge]: https://readthedocs.org/projects/logger-helper/badge/?version=latest
[build_badge]: https://travis-ci.org/vimist/logger-helper.svg?branch=master
[maintainability_badge]: https://api.codeclimate.com/v1/badges/17691babd47c3cc19e91/maintainability
[test_coverage_badge]: https://api.codeclimate.com/v1/badges/17691babd47c3cc19e91/test_coverage

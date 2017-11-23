Documentation build, testing and linting for the `master` branch.

[![Build Status](https://travis-ci.org/vimist/logger-helper.svg?branch=master)](https://travis-ci.org/vimist/logger-helper) [![Maintainability](https://api.codeclimate.com/v1/badges/17691babd47c3cc19e91/maintainability)](https://codeclimate.com/github/vimist/logger-helper/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/17691babd47c3cc19e91/test_coverage)](https://codeclimate.com/github/vimist/logger-helper/test_coverage)

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
pip install git+https://github.com/vimist/logger-helper
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

For more information, be sure to read the documentation. If you clone this
repository and install [invoke](http://www.pyinvoke.org), you can serve the
documentation locally with `invoke serve-docs`.

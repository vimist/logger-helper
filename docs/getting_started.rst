.. _getting-started:

Getting Started
===============

.. toctree::
   :maxdepth: 2

Please read the :ref:`installation` section before going any further.

Importing and Setup
-------------------

Import ``logging`` and the :class:`logger_helper.LoggerHelper` class to get
started:

    >>> import logging
    >>> import logger_helper

Here, as an example, we're going to set up and use a simple `file handler`_ to
capture our logs, but you can (and should) configure the `logging`_ module as
you would normally (see the Python documentation on `logging configuration`_)
if you're going to use it in your own application:

    >>> logger = logging.getLogger(__name__)
    >>> handler = logging.FileHandler('/tmp/my_log.log', 'w')
    >>> logger.addHandler(handler)
    >>> logger.setLevel(logging.DEBUG)

Now we've got a basic logger configured we can create a new instance of the
:class:`logger_helper.LoggerHelper` class. Pass it the logger we want it to
write to and the level at which it should write to it with:

    >>> log = logger_helper.LoggerHelper(
    ...     logging.getLogger(__name__), logging.DEBUG)

**That's it, you're done!** (almost). The only thing that's left to do from
here is to choose the modules, classes, methods and functions to wrap!

Usage
-----

Once you have the logger configured, classes, methods and functions can all be
wrapped very simply, just use the class instance as a decorator:

    >>> @log
    >>> class MyClass:
    >>>     def method_one(self, param):
    >>>         print('Method one:', param)
    >>>         return 123
    >>>
    >>> @log
    >>> def my_function(param_1, param_2):
    >>>     print('Doing something with {} and {}'.format(param_1, param_2))
    >>>     raise Exception('Something didn\'t work out...')

After you've wrapped your classes and functions, you can use them just as you
would normally:

    >>> my_class = MyClass()
    >>> my_class.method_one('Hi')
    Method one: Hi
    >>>
    >>> try:
    ...     my_function('Blue', 'Green')
    ... except Exception as ex:
    ...     print('Caught:', ex)
    Doing something with Blue and Green
    Caught: Something didn't work out...

Now, lets take a look at ``/tmp/my_log.log`` (the handler we set up at the
beginning of this tutorial):

.. code-block:: bash

   cat /tmp/my_log.log

.. code-block:: none

   Calling __main__.MyClass.method_one(param = 'Hi')
   Returned 123 from __main__.MyClass.method_one
   Calling __main__.my_function(param_1 = 'Blue', param_2 = 'Green')
   Exception Exception occurred in __main__.my_function, "Something didn't work out..."

**Done! (for real this time)**. That's how simple it is to get started with
Logger Helper!

The `mod` Method
----------------

There is one other useful feature that Logger Helper provides, the
:meth:`logger_helper.LoggerHelper.mod` method. When it's passed a module, it
will wrap all functions and classes within it.

Assuming that we've set up our ``logger`` and ``LoggerHelper`` (as described
above) and you have ``import my_module`` in your file, we can then do the
following:

>>> log.mod(my_module) # Remember that `log` is an instance of `logger_helper.LoggerHelper`

You can also pass a list of symbols (classes/functions) that you want to wrap
within your module to limit what gets wrapped:

>>> log.mod(my_module, ['ClassOne', 'some_function'])

Further Reading
---------------

Take a look at the :meth:`logger_helper.LoggerHelper.mod`,
:meth:`logger_helper.LoggerHelper.cls`, :meth:`logger_helper.LoggerHelper.meth`
and :meth:`logger_helper.LoggerHelper.func` docstrings for more information.

.. _logging: https://docs.python.org/3/library/logging.html
.. _logging configuration: https://docs.python.org/3/howto/logging.html#configuring-logging
.. _file handler: https://docs.python.org/3/library/logging.handlers.html#filehandler

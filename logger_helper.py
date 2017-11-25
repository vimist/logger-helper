"""Logger Helper main classes and utility functions."""

import inspect
import functools


def get_callable_name(clbl):
    """Get the fully qualified name of a callable.

    Parameters:
        clbl: The callable to get the name for.

    Returns:
        str: A string representing the full path to the given callable.
    """
    return '{module}.{callable}'.format(
        module=clbl.__module__,
        callable=clbl.__qualname__)


# pylint: disable=too-many-instance-attributes
class LoggerHelper:
    """Log calls to class methods and functions."""

    def __init__(self, logger, log_level):
        """Create a new helper that writes to a specific logger.

        Parameters:
            logger (logging.Logger): The logger to write to.
            log_level (int): The log level to log at. This should be one of the
                `logging.XXXXX` constants, for example `logging.DEBUG`.

        Attributes:
            call_log_format (str): The format string to use when formatting a
                call to a callable. The available tokens are:

                 - `callable` - The name of the callable.
                 - `args` - The arguments passed to the callable. The format of
                   the arguments is defined in the `argument_format` property.

            argument_format (str): The format of each argument. The available
                tokens are:

                 - `name` - The name of the argument.
                 - `value` - The value of the argument.

            argument_separator (str): The separator to join the arguments
                together with.

            return_log_format (str): The format to log the return with. The
                available tokens are:

                 - `callable` - The name of the callable.
                 - `return_value` - The return value (after it's been run
                   through `repr`).

            exception_log_format (str): The format to log exceptions with. The
                available tokens are:

                 - `callable` - The name of the callable.
                 - `name` - The name of the exception.
                 - `message` - The exception message.
        """
        self._logger = logger
        self._log_level = log_level

        self.call_log_format = 'Calling {callable}({args})'
        self.argument_format = '{name} = {value}'
        self.argument_separator = ', '
        self.return_log_format = 'Returned {value} from {callable}'
        self.exception_log_format = (
            'Exception {name} occurred in {callable}, "{message}"')

    def _wrap_callable(self, clbl, class_method=False):
        """Wrap a callable in the decorator that performs the logging.

        Parameters:
            clbl: The callable to wrap.
            class_method (bool): Whether the callable is a class method. This
                is used to determine if we should log the first parameter if
                it's called `self`.

        Returns:
            A new callable that will perform the logging as well as the
            original action.
        """
        @functools.wraps(clbl)
        def wrapped_callable(*args, **kwargs):
            """Log calls, exceptions and return values.

            Parameters:
                args (list): The positional parameters to pass to the original
                    callable.
                kwargs (dict): The keyword parameters to pass to the original
                    callable.

            Returns:
                Whatever the original callable returns.
            """
            self._log_call(clbl, args, kwargs, class_method)

            try:
                return_value = clbl(*args, **kwargs)
            except BaseException as ex:
                self._log_exception(clbl, ex)
                raise

            self._log_return(clbl, return_value)

            return return_value

        return wrapped_callable

    def _log_call(self, clbl, args, kwargs, class_method=False):
        """Log the call to the callable.

        Note:
            The call is logged in the format defined in the instance variable
            `call_log_format`. The arguments within that are formatted using
            the `argument_format` and `argument_separator` variables.

        Parameters:
            clbl: The callable to log the call for.
            args (list): Positional parameters passed to the callable.
            kwargs (dict): Keyword parameters passed to the callable.
            class_method (bool): Whether the callable is a class method. This
                is used to determine if we should log the first parameter if
                it's called `self`.

        Returns:
            None
        """
        parameters = inspect.signature(clbl).parameters

        arg_list = []
        for i, parameter in enumerate(parameters):
            if class_method and parameter == 'self':
                continue

            try:
                val = args[i]
            except IndexError:
                try:
                    val = kwargs[parameter]
                except KeyError:
                    val = parameters[parameter].default

            arg_list.append(
                self.argument_format.format(
                    name=parameter,
                    value=repr(val)))

        log_message = self.call_log_format.format(
            callable=get_callable_name(clbl),
            args=self.argument_separator.join(arg_list))

        self._logger.log(self._log_level, log_message)

    def _log_return(self, clbl, return_value):
        """Log the return value from a callable.

        Note:
            The return value is logged in the format defined in the instance
            variable `return_log_format`.

        Parameters:
            clbl: The callable to log the return value for.
            return_value: The return value to log against the call.

        Returns:
            None
        """
        log_message = self.return_log_format.format(
            callable=get_callable_name(clbl),
            value=repr(return_value))

        self._logger.log(self._log_level, log_message)

    def _log_exception(self, clbl, exception):
        """Log the exception that was raised.

        Note:
            The log message is logged in the format defined in the instance
            variable `exception_log_format`.

        Parameters:
            clbl: The callable that the exception was raised in.
            exception (BaseException): The exception that was raised.

        Returns:
            None
        """
        log_message = self.exception_log_format.format(
            callable=get_callable_name(clbl),
            name=exception.__class__.__qualname__,
            message=str(exception))

        self._logger.log(self._log_level, log_message)

    def __call__(self, obj):
        """Wrap the class methods or functions in our decorator.

        Raises:
            TypeError: When the object isn't a class or function.

        Returns:
            The fully wrapped class or function.
        """
        if inspect.isclass(obj):
            new_obj = self.cls(obj)
        elif inspect.isfunction(obj):
            new_obj = self.func(obj)
        else:
            raise TypeError('{} is not a class or a callable.'.format(obj))

        return new_obj

    def mod(self, mod, symbols=None):
        """Wrap an entire module's classes and functions.

        Parameters:
            mod (module): The module to wrap.
            symbols (list): If this is specified, only the symbols
                (classes/functions) listed will be wrapped. Each item in the
                list should be a string.

        Returns:
            None: Nothing is returned, the class is wrapped in place.
        """
        for member_name, member in inspect.getmembers(mod):
            if ((symbols is not None and member_name not in symbols)
                    or not inspect.isclass(member)
                    and not inspect.isfunction(member)):
                continue

            member = getattr(mod, member_name)
            wrapped_member = self.__call__(member)

            setattr(mod, member_name, wrapped_member)

    def cls(self, cls):
        """Wrap a classes methods (that don't start and end with `__`).

        Parameters:
            cls: The class to wrap.

        Returns:
            `cls`: A *copy* of the given class with all of it's methods
            wrapped.
        """
        # Make a copy of the class to ensure we don't alter the original
        new_cls = type('NewBasicClass', cls.__bases__, dict(cls.__dict__))

        for member_name, member in inspect.getmembers(new_cls):
            if not callable(member) or (
                    member_name.startswith('__')
                    and member_name.endswith('__')):
                continue

            wrapped_method = self._wrap_callable(member, True)

            setattr(new_cls, member_name, wrapped_method)

        return new_cls

    def func(self, function):
        """Wrap a function.

        Parameters:
            function: The function to wrap.

        Returns:
            `function`: A wrapped *copy* of the given function.
        """
        return self._wrap_callable(function)

    def meth(self, method):
        """Wrap a method belonging to a class.

        Returns:
            `method`: A wrapped *copy* of the fiven method.
        """
        return self._wrap_callable(method, True)

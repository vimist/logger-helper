import inspect
import logging
import types
import unittest

from logger_helper import LoggerHelper
from logger_helper import get_callable_name


# pylint: disable=invalid-name,unused-argument
def basic_function(a, b, c, d=1, e=2):
    """Test Docstring."""
    return 'Test'


def exception_function():
    raise Exception('This is an exception')


class BasicClass:
    def __init__(self):
        self.value = 'Test'

    def method_1(self):
        return '{value} 1'.format(value=self.value)

    def method_2(self):
        return '{value} 2'.format(value=self.value)


class TestLoggerHelper(unittest.TestCase):
    def setUp(self):
        # Create a fake module
        self._basic_module = types.ModuleType('basic_module')
        self._basic_module.basic_function = basic_function
        self._basic_module.BasicClass = BasicClass
        self._basic_module.property = 123

        # Logs are stored here
        self._logs = []

        # Log to a list
        class CustomHandler(logging.Handler):
            def __init__(self, log_list, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self._log_list = log_list

            def emit(self, record):
                self._log_list.append(record.msg)

        # Create the logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(CustomHandler(self._logs))

        # Create the logger_helper
        self._logger_helper = LoggerHelper(self._logger, logging.DEBUG)

    def test__wrap_callable_logs_call_and_return(self):
        self._logger_helper.call_log_format = 'Calling'
        self._logger_helper.return_log_format = 'Returned'

        wrapped = self._logger_helper._wrap_callable(basic_function)
        wrapped(1, 2, 3)

        self.assertEqual(['Calling', 'Returned'], self._logs)

    def test__wrap_callable_logs_and_passes_through_exception(self):
        self._logger_helper.exception_log_format = 'Exception'

        wrapped = self._logger_helper._wrap_callable(exception_function)

        with self.assertRaises(Exception):
            wrapped()

        self.assertIn('Exception', self._logs)

    def test__wrap_callable_keeps_docstrings(self):
        wrapped = self._logger_helper._wrap_callable(basic_function)
        self.assertEqual('Test Docstring.', wrapped.__doc__)

    def test__wrap_keeps_signature(self):
        wrapped = self._logger_helper._wrap_callable(basic_function)
        self.assertEqual(
            '(a, b, c, d=1, e=2)', str(inspect.signature(wrapped)))

    def test_get_callable_name(self):
        callable_name = get_callable_name(basic_function)
        self.assertEqual('tests.basic_function', callable_name)

    def test__log_call(self):
        self._logger_helper.call_log_format = '{callable}:{args}'
        self._logger_helper.argument_format = '{name}={value}'
        self._logger_helper.argument_separator = ','

        self._logger_helper._log_call(
            basic_function, (10, 20), {'c': 40, 'd': 'Test'})

        log_record = 'tests.basic_function:a=10,b=20,c=40,d=\'Test\',e=2'

        self.assertEqual([log_record], self._logs)

    def test__log_return(self):
        self._logger_helper.return_log_format = '{value}'

        self._logger_helper._log_return(basic_function, 'Test')

        self.assertEqual(['\'Test\''], self._logs)

    def test__log_exception(self):
        self._logger_helper.exception_log_format = '{name}:{message}'

        self._logger_helper._log_exception(basic_function, Exception('Test'))

        self.assertEqual(['Exception:Test'], self._logs)

    def test___call__raises_exception_when_not_class_or_callable(self):
        with self.assertRaises(TypeError):
            self._logger_helper.__call__('Hello')

    def test___call__wraps_all_class_methods(self):
        self._logger_helper.call_log_format = '{callable}'
        self._logger_helper.return_log_format = '{value}'

        wrapped = self._logger_helper.__call__(BasicClass)

        bc = wrapped()
        bc.method_1()
        bc.method_2()

        self.assertEqual(
            [
                'tests.BasicClass.method_1', '\'Test 1\'',
                'tests.BasicClass.method_2', '\'Test 2\''
            ],
            self._logs)

    def test___call__wraps_function(self):
        self._logger_helper.call_log_format = '{callable}'
        self._logger_helper.return_log_format = '{value}'

        wrapped = self._logger_helper.__call__(basic_function)
        wrapped(1, 2, 3, 4, 5)

        self.assertEqual(['tests.basic_function', '\'Test\''], self._logs)

    def test_func_wraps_function(self):
        self._logger_helper.call_log_format = '{callable}'
        self._logger_helper.return_log_format = '{value}'

        wrapped = self._logger_helper.func(basic_function)
        wrapped(1, 2, 3, 4, 5)

        self.assertEqual(['tests.basic_function', '\'Test\''], self._logs)

    def test_meth_wraps_function(self):
        self._logger_helper.call_log_format = '{callable}'
        self._logger_helper.return_log_format = '{value}'

        wrapped = self._logger_helper.meth(basic_function)
        wrapped(1, 2, 3, 4, 5)

        self.assertEqual(['tests.basic_function', '\'Test\''], self._logs)

    def test_mod_wraps_module(self):
        self._logger_helper.call_log_format = '{callable}'
        self._logger_helper.return_log_format = '{value}'

        self._logger_helper.mod(self._basic_module)

        self._basic_module.basic_function(9, 8, 7)  # pylint: disable=no-member
        bc = self._basic_module.BasicClass()  # pylint: disable=no-member
        bc.method_1()
        bc.method_2()

        # pylint: disable=no-member
        self.assertEqual(self._basic_module.property, 123)
        self.assertEqual(
            [
                'tests.basic_function', '\'Test\'',
                'tests.BasicClass.method_1', '\'Test 1\'',
                'tests.BasicClass.method_2', '\'Test 2\'',
            ],
            self._logs)

    def test_mod_only_wraps_given_symbols(self):
        self._logger_helper.call_log_format = '{callable}'
        self._logger_helper.return_log_format = '{value}'

        # pylint: disable=no-member
        self._logger_helper.mod(self._basic_module, ['BasicClass'])

        self._basic_module.basic_function(9, 8, 7)  # pylint: disable=no-member
        bc = self._basic_module.BasicClass()  # pylint: disable=no-member
        bc.method_1()
        bc.method_2()

        # pylint: disable=no-member
        self.assertEqual(self._basic_module.property, 123)
        self.assertEqual(
            [
                'tests.BasicClass.method_1', '\'Test 1\'',
                'tests.BasicClass.method_2', '\'Test 2\'',
            ],
            self._logs)

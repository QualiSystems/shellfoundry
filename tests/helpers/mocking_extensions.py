#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
import sys

if sys.version_info >= (3, 0):
    from unittest.mock import MagicMock
else:
    from mock import MagicMock


def bootstrap():
    MagicMock.smarter_assert_called_once_with = smarter_assert_called_once_with


def _get_default_args(args, defaults):
    """Returns a dictionary of arg_name:default_values for the input function."""
    if not defaults:
        return {}

    return dict(zip(args[-len(defaults) :], defaults))


def smarter_assert_called_once_with(self, function, **kwargs):
    """The default mock package has an 'assert_called_once_with' function that has some problems that makes testing more brittle.

    First, it matches arguments too restrictively. For example, if you provide regular arguments,
    refactoring the real function to use named arguments would break test. Also, you're required to include all arguments
    so adding an optional argument to the function, would also break the test unnecessarily.
    This function is used as an extension to the mock class. Simply import the module and you'll be able to use it
    on any mock object.

    :param self: The mock object
    :param function: The function you wish to add restrictions to
    :param kwargs: This function only accepts named arguments
    :return:
    """  # noqa: E501
    assert (
        len(self.call_args_list) == 1
    ), "Function expected to be called once but was called {times} times".format(
        times=str(len(self.call_args_list))
    )

    recorded_arg_values, recorded_named_arg = self.call_args_list[0]
    expected_args = kwargs
    spec = inspect.getargspec(function)
    defaults = _get_default_args(spec.args, spec.defaults)
    function_args = [spec_arg for spec_arg in spec.args if spec_arg != "self"]

    # The function was called with a non named argument,
    # so we can only match it by index
    # so the first task is to map them to the arg name,
    # we want to have one list of name values
    # for all recorded args to validate against
    recorded_args_unified_lookup = {}

    if not recorded_arg_values == ():
        for index, recorded_arg in enumerate(recorded_arg_values):
            arg_name = function_args[index]
            recorded_args_unified_lookup[arg_name] = recorded_arg

    for named_arg in recorded_named_arg:
        recorded_args_unified_lookup[named_arg] = recorded_named_arg[named_arg]

    mundatory_args = [arg for arg in function_args if arg not in defaults]
    for mundatory_arg in mundatory_args:
        assert (
            mundatory_arg in recorded_args_unified_lookup
        ), "Invalid function call, missing mundatory value {arg}".format(
            arg=mundatory_arg
        )

    for expected_arg in expected_args:
        assert (
            expected_arg in recorded_args_unified_lookup
        ), "The argument {expected_arg} was expected but was not provided".format(
            expected_arg=expected_arg
        )

        assert (
            expected_args[expected_arg] == recorded_args_unified_lookup[expected_arg]
        ), "Mismatched arg expectation. For arg {arg_name} expected {expected_val} but found {recorded_val}".format(  # noqa: E501
            arg_name=expected_arg,
            expected_val=expected_args[expected_arg],
            recorded_val=recorded_args_unified_lookup[expected_arg],
        )

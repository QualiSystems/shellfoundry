import inspect


def smarter_assert_called_once_with(self, function, **kwargs):
    assert len(self.call_args_list) == 1, "Function expected to be called once but was called {times} times".format(
        times=str(len(self.call_args_list)))

    recorded_arg_values, recorded_named_arg = self.call_args_list[0]
    expected_args = kwargs
    spec = inspect.getargspec(function)
    function_args = [spec_arg for spec_arg in spec.args if spec_arg != 'self']

    # The function was called with a non named argument, so we can only match it by index
    # so the first task is to map them to the arg name, we want to have one list of name values
    # for all recorded args to validate against
    recorded_args_unified_lookup = {}

    if not recorded_arg_values == ():
        for index, recorded_arg in enumerate(recorded_arg_values):
            arg_name = function_args[index]
            recorded_args_unified_lookup[arg_name] = recorded_arg

    for named_arg in recorded_named_arg:
        recorded_args_unified_lookup[named_arg] = recorded_named_arg[named_arg]

    for expected_arg in expected_args:
        assert expected_args[expected_arg] == recorded_args_unified_lookup[expected_arg], \
            "Mismatched arg expectation. For arg {arg_name} expected {expected_val} but found {recorded_val}" \
                .format(arg_name=expected_arg, expected_val=expected_args[expected_arg],
                        recorded_val=recorded_args_unified_lookup[expected_arg])

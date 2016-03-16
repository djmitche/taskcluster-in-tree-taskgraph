def evaluate(expression, **args):
    """
    Evaluate a task expression in the context of a set of named variables

    The expression can either be a string containing a Python expression, or a
    function accepting keyword arguments.
    """
    if isinstance(expression, basestring):
        return eval(expression, args)
    else:
        return expression(**args)

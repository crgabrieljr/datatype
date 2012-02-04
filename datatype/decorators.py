from functools import wraps

from doctools import append_var_to_docs

from datatype.validation import failures


class BadReturnValueError(Exception):
    """Raised when `returns` decorator encounters a return value
    not matching it's given datatype."""

    # List of things that went wrong in validation
    failures = []


def returns(dfn, strict=True):
    """Make decorators to watch return values of functions to ensure
    they match the given datatype definition.

    Optional Arguments:
        strict: if false, unexpected values will not raise an exception

    Example:
        >>> @returns('int')
        ... def myfunction():
        ...     return "bad return value"
        >>> myfunction()
        Traceback (most recent call last):
        BadReturnValueError
    """
    def decorator(fn):

        # Add return-datatype info to function doc-block
        append_var_to_docs(fn, "Return datatype", dfn)

        @wraps(fn)
        def wrapped_function(*args, **kwargs):
            ret = fn(*args, **kwargs)

            # Check for failure and raise
            fails = failures(dfn, ret)
            if fails:
                bad_values = [x for x in fails
                        if 'unexpected property' not in x]
                if strict or bad_values:
                    ex = BadReturnValueError()
                    ex.failures = fails
                    raise ex

            # All is well, return as usual
            return ret
        return wrapped_function
    return decorator


def returns_iter(dfn, strict=True):
    """Validate output of iterator/generator function."""
    def decorator(fn):
        append_var_to_docs(fn, "Return datatype (iterator of)", dfn)

        @wraps(fn)
        def wrapped_function(*args, **kwargs):
            for value in fn(*args, **kwargs):
                fails = failures(dfn, value)
                if fails:
                    bad_values = [x for x in fails
                            if 'unexpected property' not in x]
                    if strict or bad_values:
                        ex = BadReturnValueError()
                        ex.failures = fails
                        raise ex
                yield value
        return wrapped_function
    return decorator


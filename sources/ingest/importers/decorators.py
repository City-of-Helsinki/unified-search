from typing import Any, Callable


def default_on_exception(func: Callable, default: Any):
    def inner():
        try:
            return func()
        except Exception as e:
            return default

    return inner()


def with_conditional(condition: Any, expression: Any, default: Any):
    def inner():
        if (lambda: condition)():
            return default_on_exception(
                expression
                if isinstance(expression, Callable)
                else (lambda: expression),
                default,
            )
        return default

    return inner()

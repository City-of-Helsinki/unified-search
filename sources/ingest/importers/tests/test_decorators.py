import pytest

from ingest.importers.decorators import default_on_exception, with_conditional


def test_default_on_exception():
    ### Test values

    default = "default"
    d = {"key": "value"}

    def __test_exception():
        raise Exception("Test raising an exception!")

    def __test_func(*args, **kwargs):
        return "success!"

    ### Test valid cases

    assert (default_on_exception(lambda: 1, default)) == 1
    assert (default_on_exception(lambda: 1 > 2, default)) == False
    assert (default_on_exception(lambda: 1 < 2, default)) == True
    assert (default_on_exception(lambda: (lambda a, b: a + b)(1, 2), default)) == 3
    assert (default_on_exception(__test_func, default)) == "success!"
    assert (
        default_on_exception(lambda: __test_func(1, 2, 3, a="a", b="b", c="c"), default)
    ) == "success!"
    assert (default_on_exception(lambda: d["key"], default)) == "value"

    # Test error cases

    assert (default_on_exception(lambda: d["keyError"], default)) == default
    assert (default_on_exception(__test_exception, default)) == default


def test_with_conditional():
    default = "default"
    assert with_conditional(1 > 0, lambda: "true", default) == "true"
    assert with_conditional(0 > 1, lambda: "true", default) == default
    (great, greater, greatest) = (1, 10, 100)
    assert (
        with_conditional(
            1 <= great < greater < greatest and greatest > great,
            lambda: "true",
            default,
        )
        == "true"
    )
    assert with_conditional(great, lambda: great, default) == great

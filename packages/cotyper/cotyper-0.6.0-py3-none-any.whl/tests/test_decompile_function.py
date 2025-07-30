import inspect
from typing import (
    List,
    Optional,
)

from pydantic import BaseModel

from cotyper import parse_json_fields
from cotyper.compose.fold import unfold_cls


class _empty:
    """Marker object for Signature.empty and Parameter.empty."""


class Baz(BaseModel):
    bar: float = 0.5


class Bar(BaseModel):
    baz: int


@parse_json_fields(("bar", Bar), ("foobar", Bar))
class Foo(BaseModel):
    bar: Bar
    bars: List[Bar]
    foobar: Optional[Bar] = None


def test_unfold():
    class Foo(BaseModel):
        bar: int
        baz: float

    class Bar(BaseModel):
        x: float
        y: float

    @unfold_cls(Foo)
    def foobar(foo: Foo, optional: bool, b: Bar):
        return foo

    expected_params = {"bar": int, "baz": float, "optional": bool, "b": Bar}
    actual_params = {
        key: p.annotation for key, p in inspect.signature(foobar).parameters.items()
    }
    assert expected_params == actual_params

    foo = Foo(bar=1, baz=0.5)
    actual_foo = foobar(bar=foo.bar, baz=foo.baz, optional=True, b=Bar(x=0.0, y=0.0))
    assert foo == actual_foo

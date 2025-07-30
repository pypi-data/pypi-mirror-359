import functools
from types import UnionType
from typing import (
    Annotated,
    Callable,
    Literal,
    TypeAlias,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    overload,
)

from pydantic import BaseModel, Discriminator, Tag, computed_field
from pydantic.fields import FieldInfo


class AutotaggableModel(BaseModel):
    @computed_field(repr=False)  # type: ignore[prop-decorator]
    @property
    def type(self) -> str:
        return type(self).__name__


Tagger: TypeAlias = Callable[[type[BaseModel]], str]


def CLASS_NAME(t: type[BaseModel]) -> str:
    return t.__name__


M = TypeVar("M", bound=BaseModel)


@overload
def autotag(
    t: type[M], /, *, field_name: str = "type", tag_value: str | Tagger = CLASS_NAME
) -> type[M]: ...
@overload
def autotag(
    *, field_name: str = "type", tag_value: str | Tagger = CLASS_NAME
) -> Callable[[type[M]], type[M]]: ...
def autotag(
    t: type[M] | None = None,
    field_name: str = "type",
    tag_value: str | Tagger = CLASS_NAME,
) -> type[M] | Callable[[type[M]], type[M]]:
    """Automatically defines a field for a class Foo that is annotated Literal["Foo"].

    - Can be used as a decorator or called as a function.
    - If the field is already defined, asserts that it is annotated as expected.
    - Raises if the field exists as a computed field.
    - If the field already exists:
      - If it is annotated as `str` or is defined as `Literal[<tag value>]` but without default=<tag value>, redefines
        the field as if it didn't exist.
      - If it already has the desired annotation and default value, does nothing.
      - Otherwise, raises AssertionError.

    >>> @autotag
    ... class A(BaseModel): ...
    >>> A()
    A()
    >>> A().type
    'A'
    >>> A().model_dump()
    {'type': 'A'}
    >>> field = A.model_json_schema()["properties"]["type"]
    >>> [field["const"]] if "const" in field else field["enum"]
    ['A']
    >>> try:
    ...     A().type = "B"
    ... except Exception as e:
    ...     assert "frozen" in str(e)
    ...     print("Failed as expected")
    Failed as expected

    >>> @autotag(field_name="kind")
    ... class B(BaseModel): ...
    >>> B().kind
    'B'
    >>> B().type
    Traceback (most recent call last):
    ...
    AttributeError: 'B' object has no attribute 'type'

    >>> @autotag
    ... class C(BaseModel):
    ...     type: str
    >>> C()
    C()
    >>> C().type
    'C'
    >>> C().__annotations__["type"]
    typing.Literal['C']
    >>> C.model_fields["type"].annotation
    typing.Literal['C']

    >>> @autotag
    ... class D(BaseModel):
    ...     type: Literal["D"]
    >>> D().type
    'D'
    >>> D.model_fields["type"].default
    'D'

    >>> @autotag
    ... class E(BaseModel):
    ...     type: int
    Traceback (most recent call last):
    ...
    AssertionError: Expected E.type to be annotated `typing.Literal['E']` or `str` but got `<class 'int'>`

    >>> @autotag
    ... class F(BaseModel):
    ...     @computed_field
    ...     @property
    ...     def type(self) -> Literal["F"]:
    ...         return "F"
    Traceback (most recent call last):
    ...
    AssertionError: Cannot autotag F since it already defines `type` as a computed field

    >>> class BaseG(BaseModel):
    ...     type: str
    >>> @autotag
    ... class G1(BaseG): ...
    >>> @autotag
    ... class G2(BaseG): ...
    >>> print(G1().type, G2().type)
    G1 G2

    >>> @autotag(tag_value=lambda t: f"tag_{t.__name__}")
    ... class H(BaseModel): ...
    >>> H().type
    'tag_H'
    >>> H().model_dump()
    {'type': 'tag_H'}

    >>> import re
    >>> @autotag(field_name="camel")
    ... @autotag(field_name="snake", tag_value=lambda t: re.sub(r"(?<!^)(?=[A-Z])", "_", t.__name__).lower())
    ... class DoubleTagged(BaseModel): ...
    >>> DoubleTagged().camel
    'DoubleTagged'
    >>> DoubleTagged().snake
    'double_tagged'
    """
    if t is None:
        return functools.partial(autotag, field_name=field_name, tag_value=tag_value)
    if not isinstance(tag_value, str):
        tag_value = tag_value(t)
    annotation = cast(type, Literal.__getitem__(tag_value))
    if field_name in t.model_computed_fields:
        raise AssertionError(
            f"Cannot autotag {t.__name__} since it already defines `{field_name}` as a computed field"
        )
    # Ignore existing field if it's not in the class's __annotations__, which indicates it was defined by a parent class.
    if field_name in t.__annotations__ and (
        existing_field := t.model_fields.get(field_name)
    ):
        if existing_field.annotation == annotation:
            if existing_field.default == tag_value:
                return t
        elif existing_field.annotation is not str:
            err = f"Expected {t.__name__}.{field_name} to be annotated `{annotation}` or `str` but got `{existing_field.annotation}`"
            raise AssertionError(err)
    # NOTE: Classes that don't define any of their own fields inherit the parent class's __annotations__ so we need
    # to assign a copy to it to avoid altering the parent class's annotations.
    t.__annotations__ = {**t.__annotations__, field_name: annotation}
    t.model_fields[field_name] = FieldInfo(
        annotation=annotation, default=tag_value, init=False, repr=False, frozen=True
    )
    t.model_rebuild(force=True)
    return t


U = TypeVar("U")


def autotagged_union(
    union: type[U], field_name: str = "type", tag_value: Tagger = CLASS_NAME
) -> type[U]:
    """
    Converts a union type to a pydantic tagged union without all the boilerplate.

    Uses `autotag` to define the discriminator field on each type in the union if it's not already
    defined.

    >>> from typing import TYPE_CHECKING
    >>> class A(BaseModel):
    ...     pass
    >>> class B(BaseModel):
    ...     pass
    >>> AorB = A | B
    >>> if not TYPE_CHECKING:
    ...     AorB = autotagged_union(AorB)
    >>> class C(BaseModel):
    ...     data: AorB
    >>> C(data=A()).model_dump()
    {'data': {'type': 'A'}}
    >>> C(data=B()).model_dump()
    {'data': {'type': 'B'}}
    >>> C.model_validate({"data": {"type": "A"}})
    C(data=A())
    >>> C.model_validate({"data": {"type": "B"}})
    C(data=B())

    >>> # Two unions that overlap but with different field names and tag values
    >>> class D(BaseModel):
    ...    pass
    >>> class E(BaseModel):
    ...    pass
    >>> class F(BaseModel):
    ...    pass
    >>> DorE = autotagged_union(D|E)

    >>> # Check that the union type includes the correct annotations
    >>> assert "tag='D'" in str(DorE) and "tag='E'" in str(DorE)
    >>> assert "discriminator='type'" in str(DorE)
    >>> # There should be no leakage between two overlapping union types
    >>> assert "tag='e'" not in str(DorE)
    >>> EorF = autotagged_union(E|F, field_name="lower_tag", tag_value=lambda t: t.__name__.lower())
    >>> assert "tag='e'" in str(EorF) and "tag='f'" in str(EorF)
    >>> assert "discriminator='lower_tag'" in str(EorF)
    >>> assert "tag='E'" not in str(EorF)
    >>> D().model_dump()
    {'type': 'D'}
    >>> E().model_dump()
    {'type': 'E', 'lower_tag': 'e'}
    >>> F().model_dump()
    {'lower_tag': 'f'}
    """
    assert get_origin(union) in (Union, UnionType), (
        f"Expected a Union or UnionType, got {union}"
    )
    types = get_args(union)
    annotated_union = Union.__getitem__(
        tuple(Annotated[t, Tag(tag_value(t))] for t in types)
    )
    for t in types:
        assert issubclass(t, BaseModel)
        autotag(t, field_name=field_name, tag_value=tag_value)

    return Annotated[annotated_union, Discriminator(field_name)]  # type: ignore[return-value]


__all__ = ["autotag", "autotagged_union"]

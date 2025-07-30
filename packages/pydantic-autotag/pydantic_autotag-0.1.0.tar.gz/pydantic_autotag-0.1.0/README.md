# pydantic-autotag

A lightweight Python library that simplifies working with tagged unions in
Pydantic by automatically adding discriminator fields to your models and
annotating union types. Using discriminators makes deserializing union types
dramatically faster since it only has to deserialize the value as the correct
type without trying all the other possible types. It also prevents any issues
arising if one value

## Installation

Install from PyPI:

```bash
uv add pydantic-autotag
```

or

```bash
pip install pydantic-autotag
```

## Features

- **Automatic tagging**: Add discriminator fields to Pydantic models with a simple decorator
- **Tagged unions**: Convert regular unions to Pydantic tagged unions with a single function call
- **Custom field names**: Use any field name for discrimination (defaults to "type")
- **Custom tags**: Use any function to generate the tag value for each class

## Usage

```python
from typing import TypeAlias, TYPE_CHECKING
from pydantic import BaseModel
from pydantic_autotag import autotagged_union

class Foo(BaseModel):
    ...

class Bar(BaseModel):
    ...

# Calling functions is not allowed in type definitions so this won't be accepted:
# FooOrBar = autotagged_union(Foo | Bar)
# Instead, define the union and then apply autotagging only when not type checking.
FooOrBar: TypeAlias = Foo | Bar

if not TYPE_CHECKING:
    FooOrBar = autotagged_union(FooOrBar)
```

You can also decorate model classes directly:

```python
from pydantic import BaseModel
from pydantic_autotag import autotag

@autotag
class Foo(BaseModel):
    ...
```

## Customization

By default, each class has a `type` field added to it and the field's value is the class name.
This can be customized by passing `field_name` and/or `tag_value` keyword arguments to `autotagged_union` or `autotag`:

```python
@autotag(field_name="name", tag_value="Happy")
class PositiveEmotion(BaseModel):
    ...
```

is equivalent to:

```python
class PositiveEmotion(BaseModel):
    name: Literal["Happy"] = Field(init=False, default="Happy", repr=False, frozen=True)
    ...
```

For unions, you must pass a function that returns the tag value for a given class:

```python
FooOrBar = autotagged_union(FooOrBar, field_name="which", tag_value=lambda c: c.__name__.lower())
```

## Type Safety

If you need to directly access the generated field and don't want your type checker to be unhappy, you can declare the field either as a `str` or as a `Literal["ExpectedTagValue"]`
and autotag will replace it at runtime just like it would if the field didn't exist. One
easy way to do this is with a base class:

```python
class MyBase(BaseModel):
    type: str

class A(MyBase):
    ...

class B(MyBase):
    ...


AorB: TypeAlias = A | B

if not TYPE_CHECKING:
    AorB = autotagged_union(AorB)
```

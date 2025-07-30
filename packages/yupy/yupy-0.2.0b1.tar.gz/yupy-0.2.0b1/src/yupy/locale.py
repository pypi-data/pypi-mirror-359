from typing import Optional, Literal, TypedDict, TypeAlias, Union, Callable, Any, List

__all__ = (
    'locale',
    'set_locale',
    'get_error_message',
    'ErrorMessage',
)

ErrorMessage: TypeAlias = Union[str, Callable[[Any | List[Any]], str]]


class Locale(TypedDict, total=False):
    const: ErrorMessage
    type: ErrorMessage
    min: ErrorMessage
    max: ErrorMessage
    length: ErrorMessage
    required: ErrorMessage
    nullable: ErrorMessage
    not_nullable: ErrorMessage
    test: ErrorMessage
    matches: ErrorMessage
    email: ErrorMessage
    url: ErrorMessage
    uuid: ErrorMessage
    lowercase: ErrorMessage
    uppercase: ErrorMessage
    le: ErrorMessage
    ge: ErrorMessage
    lt: ErrorMessage
    gt: ErrorMessage
    eq: ErrorMessage
    ne: ErrorMessage
    integer: ErrorMessage
    multiple_of: ErrorMessage
    positive: ErrorMessage
    negative: ErrorMessage
    array: ErrorMessage
    mapping: ErrorMessage
    array_of: ErrorMessage
    shape: ErrorMessage
    shape_fields: ErrorMessage
    strict: ErrorMessage
    one_of: ErrorMessage
    undefined: ErrorMessage


LocaleKey = Literal[
    "const", "type", "min", "max", "length", "required", "nullable", "not_nullable", "test", "matches",
    "email", "url", "uuid", "lowercase", "uppercase",
    "le", "ge", "lt", "gt", "eq", "ne",
    "integer", "multiple_of", "positive", "negative", "mapping", "array", "array_of", "shape",
    "shape_fields", "strict", "one_of", "undefined"
]

locale: Locale = {
    "const": lambda args: "Value is not match the const %r" % args,
    "type": lambda args: "Value is not of type %r, got %r" % args,
    "min": lambda args: "Min length must be %r" % args,
    "max": lambda args: "Max length must be %r" % args,
    "length": lambda args: "Length must be %r" % args,
    "uppercase": "Value must be an uppercase string",
    "lowercase": "Value must be a lowercase string",
    "required": "Value is required",
    "nullable": "Value can't be null",
    "not_nullable": "Value can't be null",
    "test": "Test failed",
    'matches': "Don't match regex",  # FIXME
    "email": "Value must be a valid email",
    "url": "Value must be a valid URL",
    "uuid": "Value must be a valid UUID",
    "le": lambda args: "Value must be less or equal to %r" % args,
    "ge": lambda args: "Value must be greater or equal to %r" % args,
    "lt": lambda args: "Value must be less than %r" % args,
    "gt": lambda args: "Value must be greater than %r" % args,
    "eq": lambda args: "Value must be equal to %r" % args,
    "ne": lambda args: "Value must be not equal to %r" % args,
    "positive": "Value must be positive, a.g. > 0",
    "negative": "Value must be positive, a.g. < 0",
    "integer": "Value must be valid 'int', got 'float'",
    "array": "Invalid array",
    "mapping": "Invalid mapping",
    "array_of": lambda args: "Schema must be a type of ISchema or ISchemaAdapter, got %r" % args,
    "multiple_of": lambda args: "Value must be a multiple of %r" % args,
    "shape": "'Shape' must be a type of 'Shape'",
    "shape_fields": "All shape items must have a values of type of ISchema or ISchemaAdapter",
    "strict": lambda args: "Object contains unknown keys: %s" % (", ".join(map(repr, args)),),
    "one_of": lambda args: "Must be one of %r" % args,
    "undefined": "Undefined validation error"
}


def set_locale(locale_: Optional[Locale] = None) -> Locale:
    if locale_:
        locale.update(locale_)
    return locale


def get_error_message(key: LocaleKey) -> ErrorMessage:
    return locale.get(key, "undefined")

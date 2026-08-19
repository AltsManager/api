import enum

from sqlalchemy import Enum


def str_enum(enum_cls: type[enum.Enum]) -> Enum:
    return Enum(enum_cls, native_enum=False, validate_strings=True)

from enum import Enum


__all__ = ("ChoiceEnum",)


class ChoiceEnum(Enum):
    """Base class for Django-style (value, label)  ChoiceEnum."""

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj.__value__ = value
        obj.label = label
        return obj

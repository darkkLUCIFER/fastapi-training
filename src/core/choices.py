from enum import Enum


__all__ = ('ChoiceEnum',)


class ChoiceEnum(Enum):
    """Base class for Django-style (value, label)  ChoiceEnum."""

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

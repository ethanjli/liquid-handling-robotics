"""Support for specifying interface classes.
"""
# Standard imports
import abc

class InterfaceClass(abc.ABCMeta):
    """Metaclass that allows docstring inheritance.

    References:
        https://github.com/sphinx-doc/sphinx/issues/3140#issuecomment-259704637
    """

    def __new__(mcls, classname, bases, cls_dict):
        cls = abc.ABCMeta.__new__(mcls, classname, bases, cls_dict)
        mro = cls.__mro__[1:]
        for (name, member) in cls_dict.items():
            if not getattr(member, '__doc__'):
                for base in mro:
                    try:
                        member.__doc__ = getattr(base, name).__doc__
                        break
                    except AttributeError:
                        pass
        return cls


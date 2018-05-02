"""Support for specifying interface classes.
"""
# Standard imports
import abc
from functools import update_wrapper

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

def custom_repr(repr_text):
    """Function decorator that allows setting a custom repr for a class method.

    References:
        https://stackoverflow.com/a/32215277
    """
    # the decorator itself
    def method_decorator(method):

        # Wrap the method in our own descriptor.
        class CustomReprDescriptor(object):

            def __get__(self, instance, owner):
                # Return our wrapped method when we call instance.method
                # This class encapsulates the method
                class MethodWrapper(object):
                    # Callable with custom __repr__ method
                    # Capture the instance and owner (type) from the __get__ call
                    def __init__(self):
                        self.im_self = instance
                        self.im_class = owner
                        self.im_func = method

                    # Call the wrapped method using the captured instance
                    def __call__(self, *args, **kwargs):
                        return self.im_func(self.im_self, *args, **kwargs)

                    # Capture the custom __repr__ text from the decorator call
                    def __repr__(self):
                        return '{}: {}'.format(repr(self.im_self), repr_text)
                # The call to __get__ returns our wrapped method with custom __repr__
                return update_wrapper(MethodWrapper(), method)
        # The decorator returns our custom descriptor
        return CustomReprDescriptor()
    return method_decorator

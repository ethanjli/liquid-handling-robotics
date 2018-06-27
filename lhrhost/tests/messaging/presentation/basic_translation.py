"""Shows some basic serialization/deserialization examples."""
# Standard imports
import logging

# Local package imports
from lhrhost.messaging.presentation import (
    BasicTranslator, DeserializedMessagePrinter, Message
)
from lhrhost.messaging.transport import SerializedMessagePrinter

# Logging
logging.basicConfig(level=logging.INFO)


def basic_assertions(translator):
    """Run some basic tests of serialization and deserialization."""
    deserialized = Message('foo', 123)
    assert translator.serialize(deserialized) == '<foo>(123)'
    serialized = '<foo>(123)'
    assert translator.valid_serialization(serialized)
    assert translator.deserialize(serialized) == deserialized

    deserialized = Message('foo')
    assert translator.serialize(deserialized) == '<foo>()'
    serialized = '<foo>()'
    assert translator.valid_serialization(serialized)
    assert translator.deserialize(serialized) == deserialized

    assert not translator.valid_serialization('<>(2)')
    assert not translator.valid_serialization('<v 0>()')
    assert not translator.valid_serialization('<pt1234567>(4321)')
    assert not translator.valid_serialization('<zt>(5.0)')
    assert not translator.valid_serialization('<zt>(1 2 3)')
    assert not translator.valid_serialization('<zt>(abc123)')


def print_serialized(translator):
    """Print some serializations."""
    deserialized = [
        Message('foo', 123),
        Message('v0'),
        Message('l', 0),
        Message('lbn', 1)
    ]
    for message in deserialized:
        print(message, end=' -> ')
        translator.on_deserialized_message(message)


def print_deserialized(translator):
    """Print some deserializations."""
    serialized = [
        '<foo>(123)',
        '<v0>()',
        '<l>(0)',
        '<lbn>(1)'
    ]
    for message in serialized:
        print(message, end=' -> ')
        translator.on_serialized_message(message)


def main():
    """Run some tests of BasicTranslator."""
    serialized_printer = SerializedMessagePrinter(prefix='Serialized: ')
    deserialized_printer = DeserializedMessagePrinter(prefix='Deserialized: ')
    translator = BasicTranslator(
        serialized_message_receivers=[serialized_printer],
        deserialized_message_receivers=[deserialized_printer],
    )
    basic_assertions(translator)
    print_serialized(translator)
    print_deserialized(translator)


if __name__ == '__main__':
    main()

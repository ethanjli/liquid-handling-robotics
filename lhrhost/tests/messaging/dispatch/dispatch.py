"""Shows some basic dispatch examples."""

# Local package imports
from lhrhost.messaging.dispatch import Dispatcher
from lhrhost.messaging.presentation import Message, MessagePrinter


def print_dispatcher(dispatcher):
    """Print some deserializations."""
    messages = [
        Message('e', 123),
        Message('e0', 123),
        Message('v'),
        Message('v0'),
        Message('v1'),
        Message('v2'),
        Message('v3'),
        Message('l', 0),
        Message('ll', 0),
        Message('lb', 1),
        Message('lbn', 1),
        Message('lbp', 1)
    ]
    for message in messages:
        print(message)
        dispatcher.on_message(message)


def main():
    """Run some tests of BasicTranslator."""
    printer_e = MessagePrinter(prefix='  Printer e: ')
    printer_v = MessagePrinter(prefix='  Printer v: ')
    printer_l = MessagePrinter(prefix='  Printer l: ')
    printer = MessagePrinter(prefix='  Printer: ')
    literal_dispatcher = Dispatcher(receivers={
        'e': [printer_e],
        'v0': [printer_v],
        'v1': [printer_v],
        'v2': [printer_v],
        'l': [printer_l],
        'lb': [printer_l],
        'lbn': [printer_l],
        None: [printer]
    })
    prefix_dispatcher = Dispatcher(prefix_receivers={
        'e': [printer_e],
        'v': [printer_v],
        'l': [printer_l],
        '': [printer]
    })
    print('Literal dispatcher:')
    print_dispatcher(literal_dispatcher)
    print('\nPrefix dispatcher:')
    print_dispatcher(prefix_dispatcher)


if __name__ == '__main__':
    main()

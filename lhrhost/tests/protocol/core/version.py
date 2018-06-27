"""Shows some basic version examples."""

# Local package imports
from lhrhost.messaging.presentation import Message, MessagePrinter
from lhrhost.protocol.core.version import Version, VersionPrinter, VersionProtocol


def version_tests():
    """Run some basic tests."""
    assert Version() == Version()
    assert Version(0, 0, 0) == Version(0, 0, 0)
    assert Version(0, 0, 0) != Version(1, 2, 3)
    assert Version(0, 2, 3) != Version(1, 2, 3)

    assert Version(1, 2, 3) == Version(1, 2, 3)
    assert Version(1, 2, 3) <= Version(1, 2, 3)

    assert Version(0, 2, 3) < Version(1, 2, 3)
    assert Version(0, 2, 3) <= Version(1, 2, 3)

    assert Version(1, 2, 2) < Version(1, 2, 3)
    assert Version(1, 2, 2) <= Version(1, 2, 3)

    assert Version(1, 0, 2) < Version(1, 2, 3)
    assert Version(1, 0, 2) <= Version(1, 2, 3)

    assert not Version(0, 2, 3) > Version(1, 2, 3)
    assert not Version(0, 2, 3) >= Version(1, 2, 3)

    assert not Version(1, 2, 2) > Version(1, 2, 3)
    assert not Version(1, 2, 2) >= Version(1, 2, 3)

    assert not Version(1, 0, 2) > Version(1, 2, 3)
    assert not Version(1, 0, 2) >= Version(1, 2, 3)


def print_responses(version_protocol):
    """Print version response handling behavior."""
    messages = [
        Message('v0', 1),
        Message('v1', 2),
        Message('v2', 3),
        Message('v0', None),
        Message('v0', 0),
        Message('v4', 4),
        Message('v3', 1),
        Message('v3', 1),
        Message('v0', 0)
    ]
    for message in messages:
        print(message)
        version_protocol.on_message(message)
    print('\nVersion reset')
    version_protocol.version.reset()
    messages = [
        Message('v0', 1),
        Message('v1', 0),
        Message('v2', 2)
    ]
    for message in messages:
        print(message)
        version_protocol.on_message(message)


def print_commands(version_protocol):
    """Print version command issuing behavior."""
    print('Major')
    version_protocol.request_major()
    print('Minor')
    version_protocol.request_minor()
    print('Patch')
    version_protocol.request_patch()
    print('Full')
    version_protocol.request_full()


def main():
    """Run some tests of BasicTranslator."""
    version_printer = VersionPrinter(prefix='  ')
    command_printer = MessagePrinter(prefix='  ')
    version_protocol = VersionProtocol(
        version_receivers=[version_printer],
        command_receivers=[command_printer]
    )
    version_tests()
    print('Version response handling')
    print_responses(version_protocol)
    print('\n\nVersion command issuing')
    print_commands(version_protocol)


if __name__ == '__main__':
    main()

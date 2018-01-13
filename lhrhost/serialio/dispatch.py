#!/usr/bin/env python3
"""Dispatch of messages between serial connections.

This module implements multiplexing/demultiplexing of different message
channels over a single serial connection and dispatch of received messages
to event handlers on the host.
"""

# Standard imports
from collections import defaultdict
from abc import abstractmethod
from typing import Any, Mapping, Iterable
import re

# Local package imports
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.serialio.transport import ASCIIRXListener

class Message(object):
    """A message sent over a serial connection.

    Args:
        channels: the channels which the message belongs to.
        payload: the content which the message carries.

    Attributes:
        channels (str): the channel which the message belongs to.
        payload: the content which the message carries.
    """
    def __init__(self, channel: str, payload: Any):
        self.channel = channel
        self.payload = payload

    def __repr__(self):
        return 'Message("{}", {})'.format(self.channel, self.payload)

# Message Translation

class InvalidEncodingError(ValueError):
    """Error indicating that an encoded message is malformed.

    The message may have been malformed, corrupted, or incorrectly encoded.
    """
    pass

class Translator(object, metaclass=InterfaceClass):
    """Interface for encoding and decoding messages sent over serial."""

    @abstractmethod
    def encode(message: Message) -> Any:
        """Encode a message so that it can be written to serial TX.

        Args:
            message: the :obj:`Message` to encode.

        Returns:
            The encoded message, ready to be sent over serial TX by a
            :obj:`transport.Connection`.
        """
        pass

    @abstractmethod
    def valid_encoding(encoded: Any) -> bool:
        """Checks whether a message is validly encoded.

        Args:
            encoded: the encoded message to check.

        Returns:
            Whether the encoded message is well-formed in a correct encoding,
            so that it can be decoded.
        """
        pass

    @abstractmethod
    def decode(encoded: Any) -> Message:
        """Decode a message received on serial RX.

        Args:
            encoded: the encoded message to decode.

        Returns:
            The decoded message.

        Raises:
            InvalidEncodingError: `encoded` is malformed, corrupted, or of an
                otherwise invalid encoding, or a transport error was detected.
        """
        pass

# ASCII Protocol

class ASCIITranslator(Translator, ASCIIRXListener):
    """A :class:`Translator` for a :class:`transport.ASCIIConnection`.

    Auto-translates any RX line from `on_read_line` and broadcasts the
    the corresponding :class:`Message` to listeners.

    Args:
        listeners: any listeners to immediately register.
        channel_max_len (int): max allowed length of a channel id.
        channel_start: delimiter to start the channel id of a line. If `None`
            and `channel_end` is also `None`, the channel id will be excluded
            from the line.
        channel_end: delimiter to end the channel id of a line. If `None`
            and `channel_start` is also `None`, the channel id will be excluded
            from the line.
        payload_start: delimiter to start the payload of a line.
        payload_end: delimiter to end the payload of a line.

    Attributes:
        listeners (:obj:`list` of :class:`transport.ASCIIRXListener`): the
            received :obj:`Message` listeners. Add and remove listeners to this
            attribute to update what listens for new received :obj:`Message`s.
    """
    def __init__(self, listeners: Iterable[ASCIIRXListener]=[],
                 channel_max_len: int=8,
                 channel_start: str='<', channel_end: str='>',
                 payload_start: str='[', payload_end: str=']'):
        self.listeners = [listener for listener in listeners]

        self._channel_max_len = channel_max_len
        # Delimiters
        self._channel_start = channel_start
        self._channel_end = channel_end
        self._payload_start = payload_start
        self._payload_end = payload_end

        # Pattern matching
        if self.exclude_channel_id:
            channel_id_pattern_template = '()'
        else:
            channel_id_pattern_template = ''.join([
                r'\s*', '\\', self._channel_start,
                '([a-zA-Z0-9]{0,', str(self._channel_max_len), '})',
                '\\', self._channel_end
            ])
        payload_pattern_template = ''.join([
            r'\s*', '\\', self._payload_start,
            r'([-+]?\d+(\.\d*)?)',
            '\\', self._payload_end, r'\s*'
        ])
        pattern = channel_id_pattern_template + payload_pattern_template
        print(pattern)
        self._regex = re.compile(pattern)

    @property
    def exclude_channel_id(self) -> bool:
        """Whether the translator omits/ignores channel ids."""
        return self._channel_start is None and self._channel_end is None

    # Implement Translator

    def encode(self, message: Message) -> str:
        encoded_elements = []
        if not self.exclude_channel_id:
            encoded_elements += [
                self._channel_start, message.channel, self._channel_end
            ]
        encoded_elements += [
            self._payload_start, str(message.payload), self._payload_end
        ]
        return ''.join(encoded_elements)

    def valid_encoding(self, encoded: str) -> bool:
        return self._regex.fullmatch(encoded) is not None

    def decode(self, encoded: str) -> Message:
        try:
            match = self._regex.fullmatch(encoded)
            groups = match.groups()
            return Message(groups[0], groups[1])
        except AttributeError:
            raise InvalidEncodingError("Malformed message {}".format(encoded))

    # Implement transport.ASCIIRXListener

    def on_read_line(self, line: str) -> None:
        try:
            message = self.decode(line)
        except InvalidEncodingError as exc:
            print(exc)
        for listener in self.listeners:
            listener.on_message(message)

# Message Dispatch

class MessageReceiver(object, metaclass=InterfaceClass):
    """Interface for receiving messages on some channels(s)."""

    @abstractmethod
    def on_message(message: Message) -> None:
        """Event handler for a new message received from somewhere."""
        pass

class Dispatcher(object):
    """Dispatcher to demux messages on different channels to their receivers.

    Args:
        receivers: any receivers to immediately register.

    Attributes:
        receivers (:obj:`collections.defaultdict` of :obj:`str` to :obj:`list` of :obj:`MessageReceiver`):
            receivers for messages for each stream, keyed by stream ids.
    """
    def __init__(self, receivers: Mapping[str, Iterable[MessageReceiver]]={}):
        self.receivers = defaultdict(list)
        for (channel, receivers) in receivers:
            self.receivers[channel] = [receiver for receiver in receivers]

    def dispatch(self, message: Message) -> None:
        """Broadcast a message to all receivers on the channel.

        Args:
            message: the message to broadcast.
        """
        for receiver in self.receivers[message.channel]:
            receiver.on_message(message)


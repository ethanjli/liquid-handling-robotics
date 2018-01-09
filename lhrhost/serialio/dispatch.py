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

class ASCIITranslator(Translator):
    """A :class:`Translator` for a :class:`transport.ASCIIConnection`.

    Args:
        channel_start: delimiter to start the channel id of a line.
        channel_end: delimiter to end the channel id of a line.
        payload_start: delimiter to start the payload of a line.
        payload_end: delimiter to end the payload of a line.

    Attributes:
        channel_start (str): delimiter to start the channel id of a line.
        channel_end (str): delimiter to end the channel id of a line.
        payload_start (str): delimiter to start the payload of a line.
        payload_end (str): delimiter to end the payload of a line.
    """
    def __init__(self, channel_start: str='<', channel_end: str='>',
                 payload_start: str='[', payload_end: str=']'):
        # Delimiters
        self.channel_start = channel_start
        self.channel_end = channel_end
        self.payload_start = payload_start
        self.payload_end = payload_end

        # Pattern matching
        pattern = (r'\s*' r'\{}' r'([a-zA-Z]+)' r'\{}' r'\s*'
                   r'\{}' r'([-+]?\d+(\.\d*)?)' r'\{}' r'\s*').format(
            self.channel_start, self.channel_end,
            self.payload_start, self.payload_end
        )
        self._regex = re.compile(pattern)

    # Implement Translator

    def encode(self, message: Message) -> str:
        return '{}{}{}{}{}{}'.format(
            self.channel_start, message.channel, self.channel_end,
            self.payload_start, message.payload, self.payload_end
        )

    def valid_encoding(self, encoded: str) -> bool:
        return self._regex.fullmatch(encoded) is not None

    def decode(self, encoded: str) -> Message:
        try:
            match = self._regex.fullmatch(encoded)
            groups = match.groups()
            return Message(groups[0], groups[1])
        except AttributeError:
            raise InvalidEncodingError("Malformed message {}".format(encoded))

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


"""Presentation layer interfaces.

This module implements the presentation layer in the host-peripheral messaging protocol.
"""

# Standard imports
import logging
import re
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.transport import SerializedMessageReceiver
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Message(object):
    """A message sent over a serial connection.

    Args:
        channel: the id of the channel which the message belongs to.
        payload: the content which the message carries.

    Attributes:
        channels (str): the id of the channel which the message belongs to.
        payload (int): the content which the message carries.

    """

    def __init__(self, channel: str, payload: Optional[int]=None):
        """Initialize member variables."""
        self.channel: int = channel
        self.payload: Optional[int] = payload

    def __repr__(self):
        """Provide a human-readable representation."""
        if self.payload is None:
            return 'Message("{}")'.format(self.channel, self.payload)
        else:
            return 'Message("{}", {})'.format(self.channel, self.payload)

    def __eq__(self, other):
        """Determine whether the other object is identical."""
        return self.channel == other.channel and self.payload == other.payload


# Message Translation

class InvalidSerializationError(ValueError):
    """Error indicating that a serialized message is malformed.

    The message may have been malformed, corrupted, or incorrectly serialized.
    """

    pass


class Translator(object, metaclass=InterfaceClass):
    """Interface for serializing and deserializing messages for the transport layer."""

    @abstractmethod
    def serialize(self, message: Message) -> str:
        """Serialize a message so that it can be sent over the transport layer.

        Args:
            message: the :class:`Message` to serialize.

        Returns:
            The serialized message, ready to be sent over the transport layer.

        """
        pass

    @abstractmethod
    def valid_serialization(self, serialized: str) -> bool:
        """Check whether a message is validly serialized.

        Args:
            serialized: the serialized message to check.

        Returns:
            Whether the serialized message is well-formed in a correct serialization,
            so that it can be deserialized.

        """
        pass

    @abstractmethod
    def deserialize(self, serialized: str) -> Message:
        """Deserialize a message received from the transport layer.

        Args:
            serialized: the serialized message to deserialize.

        Returns:
            The deserialized message.

        Raises:
            InvalidSerializationError: `serialized` is malformed, corrupted, or of an
                otherwise invalid serialization.

        """
        pass


# Receipt of deserialized messages

class DeserializedMessageReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives deserialized messages.

    This may include deserialized messages from self or from other sources.
    """

    @abstractmethod
    def on_deserialized_message(self, deserialized_message: Message) -> None:
        """Receive and handle a deserialized message, i.e. a :class:`Message`."""
        pass


# Type-checking names
_SerializedMessageReceivers = Iterable[SerializedMessageReceiver]
_DeserializedMessageReceivers = Iterable[DeserializedMessageReceiver]

# Printing

class DeserializedMessagePrinter(DeserializedMessageReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def on_deserialized_message(self, serialized_message: str) -> None:
        """Receive and handle a serialized message."""
        self.print(serialized_message)


# Human-Readable Presentation Protocol

class BasicTranslator(
        Translator, SerializedMessageReceiver, DeserializedMessageReceiver
):
    """A :class:`Translator` for human-readable message serializations.

    Auto-translates any line received from :meth:`on_serialized_message` and
    broadcasts the the deserialized :class:`Message` to all listeners in
    :attr:`deserialized_message_receivers`.
    Auto-translates any :class:`Message` from :meth:`on_deserialized_message`
    and broadcasts the serialized line to all listeners in
    :attr:`serialized_message_receivers`.

    Args:
        channel_max_len (int): max allowed length of a channel id.
        channel_start: delimiter to start the channel id of a line. If `None`
            and `channel_end` is also `None`, the channel id will be excluded
            from the line.
        channel_end: delimiter to end the channel id of a line. If `None`
            and `channel_start` is also `None`, the channel id will be excluded
            from the line.
        payload_start: delimiter to start the payload of a line.
        payload_end: delimiter to end the payload of a line.

    """

    def __init__(
        self,
        serialized_message_receivers: Optional[_SerializedMessageReceivers]=None,
        deserialized_message_receivers: Optional[_DeserializedMessageReceivers]=None,
        channel_max_len: int=8, channel_start: str='<', channel_end: str='>',
        payload_start: str='(', payload_end: str=')'
    ):
        """Initialize member variables."""
        self.__serialized_message_receivers: List[SerializedMessageReceiver] = []
        if serialized_message_receivers:
            self.__serialized_message_receivers = [
                receiver for receiver in serialized_message_receivers
            ]
        self.__deserialized_message_receivers: List[DeserializedMessageReceiver] = []
        if deserialized_message_receivers:
            self.__deserialized_message_receivers = [
                receiver for receiver in deserialized_message_receivers
            ]

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
                '([a-zA-Z0-9]{1,', str(self._channel_max_len), '})',
                '\\', self._channel_end
            ])
        payload_pattern_template = ''.join([
            r'\s*', '\\', self._payload_start,
            #r'(([-+]?\d+(\.\d*)?)|(\w*))',  # Allows decimal numbers and strings
            r'(([-+]?\d+)|)',  # Only allows integers
            '\\', self._payload_end, r'\s*'
        ])
        pattern = channel_id_pattern_template + payload_pattern_template
        self._regex = re.compile(pattern)

    @property
    def exclude_channel_id(self) -> bool:
        """Whether the translator omits/ignores channel ids."""
        return self._channel_start is None and self._channel_end is None

    # Implement Translator

    def serialize(self, message: Message) -> str:
        """Serialize a message so that it can be sent over the transport layer.

        Args:
            message: the :class:`Message` to serialize.

        Returns:
            The serialized message, ready to be sent over the transport layer.

        """
        serialized_elements = []
        if not self.exclude_channel_id:
            serialized_elements += [
                self._channel_start, message.channel, self._channel_end
            ]
        serialized_elements += [
            self._payload_start,
            str(message.payload) if message.payload is not None else '',
            self._payload_end
        ]
        return ''.join(serialized_elements)

    def valid_serialization(self, serialized: str) -> bool:
        """Check whether a message is validly serialized.

        Args:
            serialized: the serialized message to check.

        Returns:
            Whether the serialized message is well-formed in a correct serialization,
            so that it can be deserialized.

        """
        return self._regex.fullmatch(serialized) is not None

    def deserialize(self, serialized: str) -> Message:
        """Deserialize a message received from the transport layer.

        Args:
            serialized: the serialized message to deserialize.

        Returns:
            The deserialized message.

        Raises:
            InvalidSerializationError: `serialized` is malformed, corrupted, or of an
                otherwise invalid serialization.

        """
        try:
            match = self._regex.fullmatch(serialized)
            groups = match.groups()
            return Message(groups[0], int(groups[1]) if len(groups[1]) else None)
        except AttributeError:
            raise InvalidSerializationError('Malformed message {}'.format(serialized))

    @property
    def serialized_message_receivers(self) -> _SerializedMessageReceivers:
        """Return an iterable of objects to forward received serialized messages to."""
        return self.__serialized_message_receivers

    @property
    def deserialized_message_receivers(self) -> _DeserializedMessageReceivers:
        """Return an iterable of objects to forward received deserialized messages to."""
        return self.__deserialized_message_receivers

    # Implement transport.SerializedMessageReceiver

    def on_serialized_message(self, line: str) -> None:
        """Handle a serialized message by deserializing it and forwarding it."""
        try:
            message = self.deserialize(line)
            for receiver in self.deserialized_message_receivers:
                receiver.on_deserialized_message(message)
        except InvalidSerializationError:
            logger.error('Received malformed serialized message: {}'.fomat(line))

    # Implement DeserializedMessageReceiver

    def on_deserialized_message(self, message: Message) -> None:
        """Handle a deserialized message by serializing it and forwarding it."""
        line = self.serialize(message)
        for receiver in self.serialized_message_receivers:
            receiver.on_serialized_message(line)

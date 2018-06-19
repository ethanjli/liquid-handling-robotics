Host-Peripheral Communication Protocol
======================================

Control of the liquid-handling robot hardware is split into multiple layers of abstraction. In the most simplified view, control between the *user* and the *hardware* is passed through a high-level *host controller* and a low-level *peripheral controller* (:numref:`controllers`). The peripheral controller (abbreviated as *peripheral*) runs on an Arduino board and manages aspects of control which require precision timing for acceptable performance. The host controller (abbreviated as *host*) runs on a separate computing device and manages higher-level and/or more computationally demanding aspects of robot planning and control.

.. graphviz:: controllers.dot
   :name: controllers
   :align: center
   :caption: : Simplified functional block diagram showing the interfaces and interactions between the user, the host controller, the peripheral controller, and the hardware. The host-peripheral protocol described on this page specifies the interfaces represented by the diagram's thick edges between the host controller and the peripheral controller.

Communication between the host and the peripheral is based on passing messages over a communication link. The host sends *command messages* (abbreviated as *commands*) to - and receives *response messages* (abbreviated as *responses*) from - the peripheral, which in turn directly manages the liquid-handling robot hardware. This design can be viewed from the `client-server model <https://en.wikipedia.org/wiki/Client%E2%80%93server_model>`_ model, with the host acting as a client, the peripheral acting as a server, commands from the host equivalent to client requests, and responses from the peripheral equivalent to server responses. The protocol described on this page specifies the host and peripheral interfaces for such communication.

Overview of Protocol Layers
---------------------------
The messaging system between the host and the peripheral is partitioned into layers of abstraction roughly conforming to the layers of the `OSI model <https://en.wikipedia.org/wiki/OSI_model>`_ (:numref:`layers`):

- The lowest layer is the *physical layer*, which specifies the physical connection between the host and the peripheral. Currently, this is provided by USB.
- The next layer is the *data link layer*, for transport of raw data between the host and the peripheral. Currently, this is provided by UART.
- Above that is the *transport layer*, which serializes messages in discrete packets and which may also allow sending and receiving of other data besides messages. Currently, two transport layers are supported and interchangeable: a Firmata-based transport layer, and an ASCII-based transport layer. The transport layer also specifies the protocol for establishing a connection session for message-passing between the host and the peripheral; this role overlaps with the role of the OSI model's session layer. Once a connection session is established, messages can be passed at the presentation layer.
- Above the transport layer is the *presentation layer*, which specifies the encoding for representing messages. Currently, the protocol for this layer specifies a human-readable representation for messages.
- The final layer for the messaging protocol is the *application layer*, at which messages are sent and received. The protocol for this layer specifies the set of commands and responses which may be passed between the host and the peripheral.

.. _layers:
.. uml:: layers.uml
   :align: center
   :caption: : Examples of data sent at the application, presentation, and transport layers. Messages are sent at the application layer, serialized message strings are sent at the presentation layer, and message packets are sent at the transport layer. The transport layer consists of either an ASCII-based protocol or a Firmata-based protocol.

Any implementation of a host controller or peripheral controller will need to implement the protocols for the transport, presentation, and application layers, which together specify how a message is sent over the data link layer between the host and the peripheral (:numref:`asciilayers`).

.. graphviz:: asciilayers.dot
   :name: asciilayers
   :align: center
   :caption: : Overview of protocol layer architecture using the ASCII-based transport layer, with transmission of an echo command as an illustrative example. On the host controller, a message at the application layer is serialized into a string at the presentation layer, which is packaged in a packet at the transport layer before being sent at the data link layer to the peripheral, where it is unpacked from a transport-layer packet into a presentation-layer message string and deserialized into an application-layer message.

Transport Layer
---------------

The transport layer provides a mechanism for transmitting and receiving messages (serialized by the presentation layer) as discrete *packets* over the data link layer. Messages can only be passed once a connection session at this layer has been established by a mutual handshake between the host and the peripheral. Currently two interchangeable transport layers are specified, to provide compatibility with different hosts:

- An ASCII-based transport layer is simplest and runs with the least memory overhead on the peripheral. It allows a user (acting in place of the host application and presentation layers) to send commands and receive responses via a host computer's serial console directly, without any additional software.
- A Firmata-based transport layer enables the peripheral to communicate with host controller software which requires using Firmata to connect to the Arduino.

The transport layer specifies a character marking the end of a packet; the transport layer may also optionally specify a character or character sequence marking the start of a packet.

ASCII-Based Transport
~~~~~~~~~~~~~~~~~~~~~

In the ASCII-based transport layer, all data sent through the layer can be typed using standard ASCII characters on a keyboard and displayed literally. This layer only supports passing of messages conforming to the presentation layer protocol. A packet in this transport layer is constructed from a message (e.g. ``<e>(1234)``) by appending a newline ``\n`` character to it (e.g. ``<e>(1234)\n``); then this packet is sent over the data link layer.

A connection session is established by exchange of simple packets between the host and the peripheral. Specifically, once a connection is established at the data link layer, the peripheral will begin sending a tilde ``~\n`` ping packet to the host at a constant rate (once every 500 ms). When the peripheral receives an empty packet ``\n``, it will acknowledge this by sending an empty packet ``\n`` back to the host. At this point, the handshake is complete, and the transport layer is ready to send messages between the host and the peripheral.

Firmata-Based Transport
~~~~~~~~~~~~~~~~~~~~~~~

In the Firmata-based transport layer, all messages sent through the layer are wrapped in a custom Firmata sysex packet type. The Firmata-based transport layer also supports multiplexing of the Firmata application layer together with the messaging application layer discussed below. Specifically, this transport layer supports a minimal subset of the `core Firmata application-layer protocol <http://firmatabuilder.com/>`_, namely DigitalInputFirmata, DigitalOutputFirmata, AnalogInputFirmata, and AnalogOutputFirmata. Thus, a peripheral supporting this transport layer can also be controlled by any Firmata host controller with or without support for the full messaging protocol documented on this page.

Messages are sent and received using the reserved Firmata sysex ID ``0x0F`` byte. Because Firmata sysex packets are also wrapped with a ``START_SYSEX`` byte ``0xF0`` and an ``END_SYSEX`` byte ``0xF7``, this means that every packet for a message (e.g. ``<e>(1234)``) is constructed by prepending ``\xF0\x0F`` and appending ``0xF7`` to it (e.g. ``\xF0\x0F<e>(1234)\xF7``); then this message packet is sent over the data link layer.

A connection session is established by the exchange of empty message packets ``\xF0\x0F\xF7`` between the host and the peripheral. Specifically, until the peripheral receives an empty message packet from the host, it will only support the core Firmata protocol. Once the peripheral receives an empty message packet from the host, it will acknowledge this by sending an empty message packet back to the host. At this point, the handshake is complete, and the transport layer is ready to send messages between the host and the peripheral.

Presentation Layer
------------------

The presentation layer specifies how messages are serialized into strings for transmission over the transport layer, once a connection session has been established at the transport layer. The data in a message consists of a *channel*, which is used for routing the message to a message handler, and a *payload*, which is used by the message handler as needed.

The presentation layer serializes the *channel name* (a name corresponding to the channel, from a hierarchical namespace) and payload of a message together in a human-readable syntax. The channel name is a string, between 1 and 8 characters long (inclusive), consisting entirely of alphanumeric characters (from *a* to *z*, *A* to *Z*, and *0* to *9*). The payload is a string representing a number. The peripheral currently only accepts payloads representing a 16-bit integer (from -32,768 to 32,767 inclusive); however, in the future the peripheral may send payloads representing floating-point numbers.

The syntax for a message is always ``<channel name>(payload)``, with the channel name surrounded by angle brackets and the payload surrounded by parentheses. Note that a message's payload may be empty, in which case it is represented as an empty string (a string of length zero), which has a special semantic meaning described later. Thus, the following strings are examples of syntactically valid messages to send to the peripheral:

- ``<pkl>(1234)``
- ``<pt123456>(4321)``
- ``<v0>()``
- ``<zt>(-5)``: Numeric digits, such as ``5``, and a hyphen, namely ``-``, at the start of the payload, are considered valid characters for the payload.

And the following strings are examples of malformed (syntatically invalid) strings for command messages sent to the peripheral:

- ``<e>(123456)``: The payload in this message will silently overflow, potentially producing unexpected behavior.
   - Because the peripheral parses the payload as a 16-bit integer, the number 123,456 (which cannot be represented in only 16 bits) will silently overflow, so the peripheral will parse the payload as -7,616.
   - If you are working with a potentially large number in your payload, you can pass it to the echo command (discussed below), which will trigger a response whose payload is the value parsed by the peripheral.
   - Commands are designed to be robust to integer overflows by sanitizing their inputs, so that they will always constrain the parsed value to be within valid ranges, or so that they ignore invalid values. However, you may still get undesirable behaviors with the sanitized values.
- ``<>(2)``: Channel name cannot be an empty string. This command will be ignored by the peripheral.
   - This will always be part of the parser's behavior.
- ``<v 0>()``: Channel name can only consist of alphanumeric characters, and the peripheral's response is undefined behavior. In the current implementation:
   - All other characters are ignored on parsing, and each one triggers a warning sent over serial (not serialized as a message).
   - The command is handled as if those characters were not part of the channel name.
   - For example, ``<v 0>()`` is handled as ``<v0>()``. Additionally, if error logging is enabled on the peripheral, the peripheral will send a warning report over serial: ``W: Channel name starting with 'v' has unknown character '32'. Ignoring it!``.
- ``<pt1234567>(4321)``: Channel name is too long, and the peripheral's response is undefined behavior. In the current implementation:
   - Any extra characters beyond the 8-character limit are discarded, and each one triggers an error report sent over serial (not serialized as a message).
   - The command is handled as if those characters were not part of the channel name.
   - For example, for the message ``<pt1234567>(4321)``, the character ``7`` in the channel name will be discarded, and the command is handled as ``<pt123456>(4321)``. Additionally, if error logging is enabled on the peripheral, the peripheral will send an error line over serial: ``E: Channel name starting with 'pt123456' is too long. Ignoring extra character '55'!``.
- ``<zt>(5.0)``: Payload cannot be a floating-point number. If the channel name is handled by the peripheral, this could cause undefined behavior. In the current implementation:
   - Invalid characters such as decimal points are ignored, so the command would be interpreted as if the message had been ``<zt>(50)``.
   - Additionally, if error logging is enabled on the peripheral, the peripheral will send a warning report over serial: ``W: Payload on channel 'zt' has unknown character '46'. Ignoring it!``, which is not serialized as a message.
- ``<zt>(1ab2 3)``: Payload can only be an integer. If it contains other characters, this could cause undefined behavior. In the current implementation:
   - Invalid characters are ignored, so the command would be interpreted as if the message had been ``<zt>(123)``.
   - Additionally, if error logging is enabled on the peripheral, the peripheral will send a series of warnings over serial:

.. code-block:: none

  W: Payload on channel 'zt' has unknown character '97'. Ignoring it!
  W: Payload on channel 'zt' has unknown character '98'. Ignoring it!
  W: Payload on channel 'zt' has unknown character '99'. Ignoring it!

Application Layer
-----------------

At the application layer, the peripheral receives and handles all commands which it recognizes, takes actions based on those commands, and sends one or more responses for each command. As mentioned in the description of the presentation layer, a message consists of a channel and a payload; the peripheral will not handle or send a response to any command with a channel which it does not recognize. The peripheral handles received commands in first-come-first-served order, and it will handle every received command (as long as the peripheral recognizes the command's channel).

After a transport-level connection is established, the peripheral runs an event loop in which it:

- Updates its internal state based on sensor signals received from hardware and commands received from the host.
- Sends responses to the host based on received commands and internal state.
- Emits actuator effort signals to the hardware.

At most one command is received and handled per iteration of the peripheral's event loop. The peripheral may also send one or more response messages without having received the usual corresponding command, namely upon completion of the transport-level connection handshake and as a result of certain modes set by commands. The peripheral will not send more than one response of the same channel per iteration of the event loop, but it may send multiple responses of different channels in the same iteration of the event loop.

Design Principles
~~~~~~~~~~~~~~~~~

The peripheral is a simple high-level interpreter which performs actions specified by instructions, following the discussion of interpreters in [SaltzerKaashoek2009]_:

- Commands are the instructions specifying actions or sequences of actions for the peripheral to execute.
- The actions which the peripheral takes based on received commands consist of updating internal state, emitting actuator effort signals to hardware, and sending response messages to host.
- Different sequences of actions triggered by commands on different channels may execute concurrently, in the sense that the actions from these different sequences will be interleaved through the peripheral's event loop. For example, the peripheral may send a sequence of response messages to the host while it is also moving an actuator to a position specified by a previous command.
- If the peripheral is executing a sequence of actions due to a command from some channel but receives a subsequent command on that same channel, it will interrupt (i.e. stop executing) the previous sequence of actions from that previous command and start executing the new sequence of actions from the new command. For example, if the peripheral is in the middle of moving an actuator to some position but receives a new command to move that actuator to a new position, the peripheral will only take actions to move the actuator to the new position. Exceptions to this occur when multiple channels interact with a shared resource (represented by a separate channel), in which case they will interrupt each other; such exceptions are explicitly documented.
- Commands specifying sequences of actions will complete asynchronously, in the sense that the peripheral will send an initial response indicating that it has begun executing the sequence of actions, and - at a later time - zero or more subsequent responses on other channels as the peripheral completes subsequent actions in that sequence. For example, if the peripheral receives a command instructing it to start sending responses to the host reporting the position of an actuator at regular time intervals, the peripheral will first send a response on the same channel as the command, and then it will send responses on a different channel at the appropriate times.

Commands and responses are designed to correspond roughly to an associative memory abstraction with READ/WRITE semantics, in the spirit of the discussion of memory abstactions in [SaltzerKaashoek2009]_. Some commands trigger additional actions beyond the READ/WRITE operations specified by this memory abstraction, but all commands provide READ/WRITE semantics:

- States, parameters, and operation modes in the peripheral are internal variables uniquely named by a command/response channel specified by the protocol documentation; names for variables do not change except with protocol design changes.
- A command with an empty payload corresponds to a READ operation of the value of the peripheral's variable named by the channel. The peripheral will handle such a command by sending a response on the same channel with the value of the variable named by that channel.
- A command with a non-empty payload corresponds to a WRITE operation of the command's payload value to the variable named by the command's channel. Every command corresponding to a WRITE operation will also trigger a response from the peripheral with the value of the variable immediately after completion of the attempted WRITE operation. Thus, a command with a non-empty payload is actually a WRITE + READ operation sequence. The host can use the payload of the response to check for faults in the command specifying the WRITE operation - for example, if the payload contained an invalid value which was changed to become a valid value written to the variable.
- Some variables are read-only; for these variables, an attempted WRITE operation does not change the value of that variable.
- All variables are initialized to operational default values when the peripheral's event loop begins.

All responses from the peripheral correspond to the result of a READ operation of an internal variable, whether or not the host had previousy issued a command with READ/WRITE semantics to the peripheral on that response's channel. Commands which do not cause the peripheral to take actions beyond READ/WRITE operations are idempotent. However, as mentioned above, some commands trigger additional actions beyond READ/WRITE operations and thus have further effects on the peripheral:

- Some commands correspond to execution of a WRITE operation of the variable specified by the command channel, followed by a READ operation of that variable, followed by additional actions. For example, a command instructing the peripheral to perform a hard reset will cause the peripheral to send a response on the same channel indicating that the peripheral is about to perform a hard reset, after which the peripheral will perform a hard reset.
- The additional actions specified by such commands may also include additional WRITE and/or READ operations. For example, a command instructing the peripheral to move an actuator to a specified position will set the target position of that actuator (WRITE), cause the peripheral to respond with the updated value of that target position (READ), set the actuator positioning mode (additional action for an implicit WRITE), cause the peripheral to respond with the updated value of that mode (additional action for an implicit READ), and cause the peripheral to adjust actuator effort signals to move the actuator towards that target position (additional actions).
- Changes to internal variables resulting from those additional actions will be visible through other commands corresponding to READ operations. For example, a command instructing the peripheral to move an actuator to a specified position will also cause a sequence of updates to an internal variable whose value is the current position of the actuator, which the host can query through a READ command.
- Such changes to internal variables may also be reported in responses from the peripheral which are not directly prompted by host commands, when such behavior is enabled by a mode in the peripheral. Such modes can be written to and read from by commands with READ/WRITE semantics. For example, if the appropriate mode is enabled (either by default or by a WRITE command for that mode), the peripheral will send a response to the host with the final position of the actuator when the actuator stops moving; and that response will be on the same channel as a READ response for the internal variable whose value is current position of the actuator.

These design principles were chosen towards the principle of least astonishment, and informed by experiences with an earlier version of the protocol in which inconsistent command semantics produced an unintuitive interface.

Messaging Protocol
~~~~~~~~~~~~~~~~~~

At the application layer, all peripherals must support the :doc:`/messages/core`, which provides basic communication functionality. Additionally, all peripherals must support either the minimal subset of the Firmata application-layer protocol provided by the Firmata-based transport layer or the :doc:`/messages/board`; either application-layer protocol subset allows control of the built-in LED on the peripheral, along with reading of hardware pin values. Note that the minimal subset of the Firmata application-layer protocol also enables writing of values to hardware pins, while the Board Protocol Subset currently does not.

Overview of Peripheral States
-----------------------------

At a simplified level, the peripheral's externally-visible behavior can be described as a hierarchical state machine (:numref:`peripheral`). After it is first turned on, the peripheral runs a setup routine and enters the **ConnectionHandshake** state. It remains in this state, looping to establish a transport-layer connection session with the host. When a connection session is established, the peripheral will proceed to the **Operational** state.

In the **Operational** state, the peripheral loops and:

- Updates its substates and internal state variables based on sensor signals received from hardware and commands received from the host.
- Emits actuator effort signals to the hardware.

An **Operational** peripheral can also transition back into the **ConnectionHandshake** state by restarting when it receives a ``<r>(...)`` reset command, as if the hardware reset button of the Arduino running the peripheral controller has been pressed. Command syntax, and the semantics of this reset command, are described later.

.. _peripheral:
.. uml:: peripheral.uml
   :align: center
   :caption: : Overview of peripheral controller's behavior. The peripheral starts by entering the **ConnectionHandshake** state and transitions between the **ConnectionHandshake** and **Operational** states based on commands received from the host.

The **Operational** state is actually a superstate with several orthogonal regions, each of which controls a single axis of the robot hardware and can be thought of as its own independent state machine. Thus, we will refer to each orthogonal region of the **Operational** superstate as an *axis controller*. Each axis controller receives all command messages received by the peripheral and is able to send response messages to the host. Each axis controller also generally behaves the same way (exceptions are documented later), follows the standard command/response message syntax, and has the same command/response protocol, so we will next discuss command/response syntax in the **Operational** state.

References
----------

.. [SaltzerKaashoek2009] Saltzer JH, Kaashoek MF. Principles of Computer System Design: An Introduction. 1st ed. Burlington (MA): Morgan Kaufmann Publishers; c2009. Chapter 2, Elements of Computer System Organization; p. 43-114.

Core Protocol
=============

All peripherals must support the core application-layer protocol, which provides basic functionality. Channels are organized hierarchically, and the names of child channels contain the names of their parent channels as prefixes. Each level in the hierarchy corresponds to either one character of the channel name or a multi-digit number.

All channels support a READ command which simpy causes the peripheral to send a READ response on that same channel, so READ commands are only explicitly documented for channels which are READ-only.

Here are the channels specified by the core protocol:

Echo
----

- **Channel name**: `e`
- **Description**: This command allows the host to test its connection to the peripheral by sending an Echo command with a payload to the peripheral; the peripheral will send a response with the same peripheral it just received. This command also allows the host to test how its payload will be parsed by the peripheral.
- **Semantics**: READ/WRITE

  - **WRITE+READ command**: If payload is provided in the command, the peripheral uses it to set the internal variable named by the Echo channel to the payload's value, and then the peripheral sends a READ response.
  - **READ response**: The peripheral sends a response on the Echo channel with the latest value of the internal variable named by the Echo channel.

.. _echo:
.. uml:: echo.uml
   :align: center
   :caption: : Examples of commands and responses associated with the Echo channel.

Reset
-----

- **Channel name**: `r`
- **Description**: This command instructs the peripheral to perform a hard reset.
- **Semantics**: READ/WRITE + actions

  - **WRITE+READ+Actions command**: If the payload is `1`, the peripheral will send a READ response and then perform a hard reset by executing the actions described below. Otherwise, the peripheral will send a READ response and do nothing.
  - **READ response**: The peripheral sends a response on the Reset channel with payload `1`, if the peripheral is about to perform a hard reset, or else with payload `0`.
  - **Actions**: The peripheral will enter a brief infinite loop which blocks the peripheral's event loop and causes an internal watchdog timer in the peripheral to hard reset the entire peripheral, including resetting the host-peripheral connection.

.. _reset:
.. uml:: reset.uml
   :align: center
   :caption: : Examples of commands, responses, and actions associated with the Reset channel.

Version
-------

- **Child channels**:

  - Version/Major
  - Version/Minor
  - Version/Patch

- **Channel names**:

  - Version: `v`

    - Version/Major: `v0`
    - Version/Minor: `v1`
    - Version/Patch: `v2`

- **Description**: These commands allow the host to query the peripheral for its protocol version. The full version has three components (major, minor, patch), and so the Version/Major, Version/Minor, and Version/Patch child channels (each with their own channel name) enable querying the three respective components individually. The Version channel can also be used to query the three components together.
- **Semantics** for child channels: READ

  - **READ command**: The peripheral simply sends a READ response to any command on the Version/Major, Version/Minor, and Version/Patch channels.
  - **READ response**: The peripheral sends a response with the version component's value as the payload for the version component named by the (child) channel.

- **Semantics** for Version channel: READ

  - **READ command**: The peripheral sequentially sends a READ response to any command on Version channel.
  - **READ response**: The peripheral sequentially sends the READ responses for Version/Major, Version/Minor, and Version/Patch.

.. _version:
.. uml:: version.uml
   :align: center
   :caption: : Examples of commands and responses associated with the Version channel and its child channels.

BuiltinLED
----------

- **Child channels**:

  - BuiltinLED/Blink (child channels of BuiltinLED/Blink documented below)

- **Channel names**:

  - BuiltinLED: `l` (the lower-case letter "L")

    - BuiltinLED/Blink: `lb` (names of child channels of BuiltinLED/Blink documented below)

- **Description**: These commands allow the host to control the built-in LED (on pin 13) of the Arduino board.
- **Semantics** for child channels documented below.
- **Semantics** for BuiltinLED channel: READ/WRITE + Actions

  - **WRITE+READ+Actions command**: If the payload is `1`, the peripheral will set the built-in LED to HIGH and send a READ response. If the payload is `0`, the peripheral will set the built-in LED to LOW and send a READ response. Otherwise, the peripheral will send a READ response and do nothing.
  - **READ response**: The peripheral sends a response on the BuiltinLED channel with payload `1` if the built-in LED is HIGH and `0` if the built-in LED is LOW.
  - **Actions**: If the WRITE+READ+ACTIONS command has a valid payload, the peripheral will set the state of the built-in LED accordingly.

.. _builtinled:
.. uml:: builtinled.uml
   :align: center
   :caption: : Examples of commands and responses associated with the BuiltinLED channel.

BuiltinLED/Blink
~~~~~~~~~~~~~~~~

- **Child channels**:

  - BuiltinLED/Blink/HighInterval
  - BuiltinLED/Blink/LowInterval
  - BuiltinLED/Blink/Periods
  - BuiltinLED/Blink/Notify

- **Channel names**:

  - BuiltinLED/Blink: `lb`

    - BuiltinLED/Blink/HighInterval: `lbh`
    - BuiltinLED/Blink/LowInterval: `lbl`
    - BuiltinLED/Blink/Periods: `lbp`
    - BuiltinLED/Blink/Notify: `lbn`

- **Description**: These commands allow the host to blink the built-in LED:

  - BuiltinLED/Blink instructs the peripheral to start or stop blinking the built-in LED.
  - BuiltinLED/Blink/HighInterval and BuiltinLED/Blink/LowInterval together specify the amounts of time (in milliseconds) the LED will be on and off, respectively, while the LED blinks.
  - BuiltinLED/Blink/Periods specifies the number of periods the LED will blink for, before turning off.
  - BuiltinLED/Blink/Notify sets the blinking notification mode - when it is enabled and the built-in LED is blinking, the peripheral will send a BuiltinLED READ response every time the built-in LED goes to HIGH or LOW.

- **Semantics** for child channels: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the variable named by the child channel with the value specified in the payload and sends a READ response with the new value of the variable:

    - BuiltinLED/Blink/HighInterval and BuiltinLED/Blink/LowInterval: the payload's value must be a positive number (in milliseconds) for the corresponding variable to be updated with it; otherwise, the corresponding variable will remain at its previous value.
    - BuiltinLED/Blink/Periods: if the payload's value is negative, then the LED will blink forever (at least until a BuiltinLED/Blink command is set to stop blinking). If the payload's value is nonnegative, then the LED will blink for that number of HIGH/LOW cycles before the LED stops blinking and stays at LOW.
    - BuiltinLED/Blink/Notify: if the payload is `1`, the peripheral will enable the blinking notification mode. If the payoad is `0`, the peripheral will disable the blinking notification mode. Otherwise, the mode will not change from its previous value.

  - **READ response**: The peripheral sends a response with the whose payload is the value for the blinking parameter/mode named by the (child) channel.

- **Semantics** for BuiltinLED/Blink channel: READ/WRITE + Actions

  - **WRITE+READ+Actions command**: If the payload is `1`, the peripheral will start blinking the built-in LED and send a READ response. If the payload is `0`, the peripheral will stop blinking the built-in LED and send a READ response. Otherwise, the peripheral will send a READ response and do nothing. After completion of every HIGH/LOW blink cycle, if the variable associated with BuiltinLED/Blink/Periods is nonnegative, that variable is decremented by `1`.
  - **READ response**: The peripheral sends a response on the BuiltinLED/Blink channel with payload `1` if the built-in LED is blinking and `0` if the built-in LED is not blinking.

.. _builtinled_blink:
.. uml:: builtinled_blink.uml
   :align: center
   :caption: : Examples of commands and responses associated with the BuiltinLED/Blink channel.

IOPins
------

- **Child channels**:

  - IOPins/Analog

    - IOPins/Analog/0
    - IOPins/Analog/1
    - IOPins/Analog/2
    - IOPins/Analog/3

  - IOPins/Digital

    - IOPins/Digital/0
    - IOPins/Digital/1
    - IOPins/Digital/2
    - IOPins/Digital/3
    - IOPins/Digital/4
    - IOPins/Digital/5
    - IOPins/Digital/6
    - IOPins/Digital/7
    - IOPins/Digital/8
    - IOPins/Digital/9
    - IOPins/Digital/10
    - IOPins/Digital/11
    - IOPins/Digital/12
    - IOPins/Digital/13

- **Channel names**:

  - IOPins: `i`

    - IOPins/Analog: `ia`

      - IOPins/Analog/0: `ia0`
      - IOPins/Analog/1: `ia1`
      - IOPins/Analog/2: `ia2`
      - IOPins/Analog/3: `ia3`

    - IOPins/Digital: `id`

      - IOPins/Digital/0: `id0`
      - IOPins/Digital/1: `id1`
      - IOPins/Digital/2: `id2`
      - IOPins/Digital/3: `id3`
      - IOPins/Digital/4: `id4`
      - IOPins/Digital/5: `id5`
      - IOPins/Digital/6: `id6`
      - IOPins/Digital/7: `id7`
      - IOPins/Digital/8: `id8`
      - IOPins/Digital/9: `id9`
      - IOPins/Digital/10: `id10`
      - IOPins/Digital/11: `id11`
      - IOPins/Digital/12: `id12`
      - IOPins/Digital/13: `id13`

- **Description**: These commands allow the host to read the value of a specified pin of the peripheral. Note that IOPins, IOPins/Analog, and IOPins/Digital are not currently used for messaging - only the child channels of IOPins/Analog and IOPins/Digital are used. For more complete pin I/O functionality, it is recommended to use the Firmata-based transport layer, which enables support for more advanced pin modes, notification of pin value changes, and writing to pins.
- **Semantics** for child channels: READ

  - **READ command**: The peripheral simply sends a READ response to any command which is a child of IOPins/Analog or IOPins/Digital.
  - **READ response**: The peripheral performs an analog read of an analog pin (for a message on a child channel of IOPins/Analog) or a digital read of a digital pin (for a message on a child channel of IOPins/Digital) sends a response with that reading as the payload for the pin named by the (child) channel. Analog reads produce values in range 0-1023, inclusive; digital reads produce values in the set {0, 1}.

.. _IOPins:
.. uml:: iopins.uml
   :align: center
   :caption: : Examples of commands and responses associated with the child chnnels of the IOPins/Analog and IOPins/Digital channels.

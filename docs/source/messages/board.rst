Board Protocol Subset
=====================

Peripherals using the ASCII-based transport layer are required to support the Board protocol subset, which provides basic hardware pin functionality for Arduino boards. The Board protocol subset should only be excluded if the peripheral does not have enough memory to support it or if the peripheral is running a Firmata-based transort layer, which also provides application-layer functionality redundant to (and more complete than) the Board protocol subset. Channels are organized hierarchically, and the names of child channels contain the names of their parent channels as prefixes. Each level in the hierarchy corresponds to either one character of the channel name or a multi-digit number.

All channels support a READ command which simply causes the peripheral to send a READ response on that same channel, so READ commands are only explicitly documented for channels which are READ-only.

Here are the channels specified by the Board protocol subset:

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

  - **WRITE+READ+Actions command**: If the payload is `1`, the peripheral will set the built-in LED to HIGH and send a READ response. If the payload is `0`, the peripheral will set the built-in LED to LOW and send a READ response. If the payload is either `0` or `1` and the built-in LED was blinking, this command will interrupt the blinking first, so that a READ command on the BuiltinLED/Blink channel will return `0`. Otherwise, the peripheral will send a READ response and do nothing.
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

  - **READ response**: The peripheral sends a response whose payload is the value for the blinking parameter/mode named by the (child) channel.

- **Semantics** for BuiltinLED/Blink channel: READ/WRITE + Actions

  - **WRITE+READ+Actions command**: If the payload is `1`, the peripheral will start blinking the built-in LED and send a READ response; this blinking will interrupt the previous state on the BuiltinLED channel. If the payload is `0`, the peripheral will stop blinking the built-in LED and send a READ response. Otherwise, the peripheral will send a READ response and do nothing. After completion of every HIGH/LOW blink cycle, if the variable associated with BuiltinLED/Blink/Periods is nonnegative, that variable is decremented by `1`. If that variable becomes `0`, then its value is reset to `-1`, blinking stops, and the peripheral sends a READ response for BuiltinLED/Blink and a READ response for BuiltinLED/Blink/Periods.
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
- **Semantics** for child channels: READ-only

  - **READ command**: The peripheral simply sends a READ response to any command which is a child of IOPins/Analog or IOPins/Digital.
  - **READ response**: The peripheral performs an analog read of an analog pin (for a message on a child channel of IOPins/Analog) or a digital read of a digital pin (for a message on a child channel of IOPins/Digital) sends a response with that reading as the payload for the pin named by the (child) channel. Analog reads produce values in range 0-1023, inclusive; digital reads produce values in the set {0, 1}.

.. _IOPins:
.. uml:: iopins.uml
   :align: center
   :caption: : Examples of commands and responses associated with the child chnnels of the IOPins/Analog and IOPins/Digital channels.

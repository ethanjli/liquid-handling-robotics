Core Protocol Subset
====================

All peripherals must support the Core protocol subset, which provides basic protocol functionality. Channels are organized hierarchically, and the names of child channels contain the names of their parent channels as prefixes. Each level in the hierarchy corresponds to one character of the channel name.

All channels support a READ command which simpy causes the peripheral to send a READ response on that same channel, so READ commands are only explicitly documented for channels which are READ-only.

Here are the channels specified by the Core protocol subset:

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


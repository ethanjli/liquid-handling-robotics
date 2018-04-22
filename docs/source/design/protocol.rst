Host-Peripheral Protocol
========================

Control of the liquid-handling robot hardware is split into multiple layers of abstraction. In the most simplified view, control between the *user* and the *hardware* is passed through a high-level *host controller* and a low-level *peripheral controller* (:numref:`controllers`). The peripheral controller (abbreviated as *peripheral*) runs on an Arduino board and manages aspects of control which require precision timing for acceptable performance. The host controller (abbreviated as *host*) runs on a separate computing device and manages higher-level and/or more computationally demanding aspects of robot planning and control.

.. graphviz:: controllers.dot
   :name: controllers
   :align: center
   :caption: : Simplified functional block diagram showing the interfaces and interactions between the user, the host controller, the peripheral controller, and the hardware. The host-peripheral protocol described on this page specifies the interfaces represented by the diagram's thick edges between the host controller and the peripheral controller.

The host gives *command messages* (abbreviated as *commands*) to - and receives *response messages* (abbreviated as *responses*) from - the peripheral, which in turn directly manages the liquid-handling robot hardware. These two controllers must communicate with each other over a serial connection, and the protocol described on this page specifies the host and peripheral interfaces for such communication.

Overview of Peripheral States
-----------------------------

At a simplified level, the peripheral controller's externally-visible behavior can be described as a hierarchical state machine (:numref:`peripheral`). After it is first turned on, the peripheral runs a setup routine and enters the **SerialHandshake** state. It remains in this state, looping and sending out a tilde ``~`` ping character over the serial connection at a constant rate. When the peripheral receives a newline ``\n`` ping reply character from the host, it will proceed to the **Operational** state. In the **Operational** state, the peripheral loops and:

- Updates its substates and internal state variables based on sensor signals received from hardware and serial commands received from the host.
- Emits actuator effort signals to the hardware.

An **Operational** peripheral can also transition back into the **SerialHandshake** state by restarting when it receives a ``<r>[...]`` reset command, as if the hardware reset button of the Arduino running the peripheral controller has been pressed. Command syntax, and the semantics of this reset command, are described later.

.. _peripheral:
.. uml:: peripheral.uml
   :align: center
   :caption: : Overview of peripheral controller's behavior. The peripheral starts by entering the **SerialHandshake** state and transitions between the **SerialHandshake** and **Operational** states based on serial inputs received from the host.

The **Operational** state is actually a superstate with several orthogonal regions, each of which can controls a single axis of the robot hardware and can be thought of as its own independent state machine. Thus, we will refer to each orthogonal region of the **Operational** superstate as an *axis controller*. Each axis controller receives all command messages received by the peripheral and is able to send response messages to the host. Each axis controller also generally behaves the same way (exceptions are documented later), follows the standard command/response message syntax, and has the same command/response protocol, so we will next discuss command/response syntax in the **Operational** state.

Command/Response Message Syntax
-------------------------------

Any command message received (or response message sent) by an **Operational** peripheral follows a standard syntax. Messages are 


Host-Peripheral Protocol
========================

Control of the liquid-handling robot hardware is split into multiple layers of abstraction. In the most simplified view, control between the *user* and the *hardware* is passes through a high-level *host controller* and a low-level *peripheral controller* (:numref:`controllers`). The peripheral controller (abbreviated as *peripheral*) runs on an Arduino board and manages aspects of control which require precision timing for acceptable performance. The host controller (abbreviated as *host*) runs on a separate computing device and manages higher-level aspects of robot planning and control.

.. graphviz:: controllers.dot
   :name: controllers
   :align: center
   :caption: : Simplified functional block diagram showing the interfaces and interactions between the user, the host controller, the peripheral controller, and the hardware. The host-peripheral protocol described on this page specifies the interfaces represented by the diagram's thick edges between the host controller and the peripheral controller.

The host gives *command messages* (abbreviated as *commands*) to - and receives *response messages* (abbreviated as *responses*) from - the peripheral, which in turn directly manages the liquid-handling robot hardware. These two controllers must communicate with each other over a serial connection, and the protocol described on this page specifies the host and peripheral interfaces for such communication.

Peripheral Operation States
---------------------------

At a high level, the peripheral controller's externally-visible behavior can be described as a hierarchical state machine.




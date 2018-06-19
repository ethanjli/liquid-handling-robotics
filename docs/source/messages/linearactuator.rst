LinearActuator Protocol Subset
==============================

Peripherals implement at least one instance of the LinearActuator protocol subset to provide linear actuator control functionality for control of liquid-handling robotics hardware. Channels are organized hierarchically, and the names of child channels contain the names of their parent channels as prefixes. Each level in the hierarchy corresponds to one character of the channel name. Peripherals may implement multiple instances of the LinearActuatorProtocol subset on multiple distinct top-level parent channels, enabling concurrent independent control of different linear actuators in the robotics hardware.

All channels support a READ command which simply causes the peripheral to send a READ response on that same channel, so READ commands are only explicitly documented for channels which are READ-only.

Here are the channels specified by the LinearActuator protocol subset:

LinearActuator
--------------

- **Child channels**:

  - LinearActuator/Position (its child channels are documented below)
  - LinearActuator/SmoothedPosition (its child channels are documented below)
  - LinearActuator/Motor (its child channels are documented below)
  - LinearActuator/FeedbackController (its child channels are documented below)

- **Channel names**:

  - LinearActuator: a unique character assigned per linear actuator. Pipettor Axis: `p`, Z-Axis: `z`, Y-Axis: `y`, X-Axis: `x`. In documentation below, a `_` underscore character is used as a placeholder for this character.

    - LinearActuator/Position: `_p` (names of its child channels are documented below)
    - LinearActuator/SmoothedPosition: `_s` (names of its child channels are documented below)
    - LinearActuator/Motor: `_m` (names of its child channels are documented below)
    - LinearActuator/FeedbackController: `_f` (names of its child channels are documented below)

- **Description**: These commands allow the host to control a linear actuator of the liquid-handling robot.
- **Semantics** for child channels documented below.
- **Semantics** for LinearActuator channel: READ-only

  - **READ command**: The peripheral simply sends a READ response.
  - **READ response**: The peripheral sends a response on the LinearActuator channel with payload `1` if the actuator is operating in direct motor duty control mode with a nonzero duty, `2` if the actuator is operating in position feedback control mode, `0` if the actuator is operating in direct motor duty control mode with a null (zero) duty, `-1` if the actuator's controller has stopped from a motor stall, `-2` if the actuator's controller has stopped from convergence to a feedback control target, and `-3` if the actuator's controller has stopped from a timeout. Negative payloads correspond to stopped actuator states where the controller has stopped running, while positive payloads correspond to moving actuator states where the controller is still running, and null (zero) payload corresponds to the stopped actuator state where the controller was initially instructed to stop the actuator.

LinearActuator/Position
-----------------------

- **Child channels**:

  - LinearActuator/Position/Notify (its child channels are documented below)

- **Channel names**:

  - LinearActuator/Position: `_p`

    - LinearActuator/Position/Notify: `_pn` (names of its child channels are documented below)

- **Description**: These commands relate to tracking of the (raw values from the) position sensor in the linear actuator.

  - LinearActuator/Position represents the raw values of the position sensor.
  - LinearActuator/Position/Notify provides functionality for the peripheral to send raw values of the position sensor to the host.

- **Semantics** for child channels documented below.

- **Semantics** for LinearActuator/Position channel: READ-only

  - **READ command**: The peripheral simply sends a READ response.
  - **READ response**: The peripheral sends a response on the LinearActuator/Position channel with a payload whose value is the current raw position reading from the linear actuator's position sensor.

LinearActuator/Position/Notify
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Child channels**:

  - LinearActuator/Position/Notify/Interval
  - LinearActuator/Position/Notify/ChangeOnly
  - LinearActuator/Position/Notify/Number

- **Channel names**:

  - LinearActuator/Position/Notify: `_pn`

    - LinearActuator/Position/Notify/Interval: `_pni`
    - LinearActuator/Position/Notify/ChangeOnly: `_pnc`
    - LinearActuator/Position/Notify/Number: `_pnn`

- **Description**: These commands relate to notification of the host of updates to the (raw values from the) position sensor in the linear actuator.

  - LinearActuator/Position/Notify sets the position notification mode - when the payload is `0`, the peripheral will not notify the host of updated positions; when the payload is `1`, the peripheral will notify the host of updated positions no more than once every *n* iterations of the peripheral's event loop, where *n* is specified by LinearActuator/Position/Notify/Interval; when the payload is `2`, the peripheral will notify the host of updated positions no more than once every approximately *n* milliseconds, where *n* is specified by LinearActuator/Position/Notify/Interval.
  - LinearActuator/Position/Notify/Interval specifies the interval between position update notifications.

    - When LinearActuator/Position/Notify is in the mode to notify the host no more than once every *n* iterations of the peripheral's event loop, the variable corresponding to this channel specifies *n*. The timing of this notification interval is approximate in that the timing between different iterations of the peripheral's event loop may vary slightly depending on amounts of data transmitted/received over the transport layer of communications between the host and the peripheral.
    - When LinearActuator/Position/Notify is in the mode to notify the host no more than once every *n* milliseconds, the variable corresponding to this channel specifies *n*. The timing of this notification interval is approximate in that there is a timer which is checked against *n* once per iteration of the peripheral's event loop, and a position update notification will only be sent once the timer exceeds *n*.
    - In either case, if LinearActuator/Position/ChangeOnly is enabled, the peripheral will not send position update notifications when the position has not changed, which will decrease the notification interval below *n*.

  - LinearActuator/Position/Notify/ChangeOnly specifies whether the peripheral will avoid sending position update notifications when the position hasn't changed, to reduce the number of messages sent from the peripheral to the host.
  - LinearActuator/Position/Notify/Number specifies the number of position update notifications the peripheral will send, before it stops sending position update notifications.

- **Semantics** for child channels: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the variable named by the child channel with the value specified in the payload and sends a READ response with the new value of the variable:

    - LinearActuator/Position/Notify/Interval: the payload's value must be a positive number for the variable to be updated with it; otherwise, the variable will remain at its previous value.
    - LinearActuator/Position/Notify/ChangeOnly: if the payload is `1`, the peripheral will not send position update notifications when the position does not change. If the payoad is `0`, the peripheral will send position update notifications regardless of whether the position has changed. Otherwise, the mode will not change from its previous value.
    - LinearActuator/Position/Notify/Number: if the payload's value is negative, then the peripheral will send position notification updates forever (at least until a LinearActuator/Position/Notify command is sent instructing the peripheral to stop sending position updates). If the payload's value is nonnegative, then the peripheral will send that number of position update notifications before the peripheral stops sending position update notifications.

  - **READ response**: The peripheral sends a response whose payload is the value for the position update notification parameter named by the (child) channel.

- **Semantics** for LinearActuator/Position/Notify channel: READ/WRITE + Actions

  - **WRITE+READ+Actions command**: If the payload is `1` or `2`, the peripheral will send a READ response and start sending position update notifications on the LinearActuator/Position channel based on the parameters specified by the payload and the child channels of LinearActuator/Position/Notify. If the payload is `0`, the peripheral will stop sending position update notifications and send a READ response. Otherwise, the peripheral will send a READ response and do nothing. After every position update notification is sent, if the variable associated with LinearActuator/Position/Notify/Number is nonnegative, that variable is decremented by `1`. If that variable becomes `0`, then its value is reset to `-1`, sending of position update notifications stops, and the peripheral sends a READ response for LinearActuator/Position/Notify and a READ response for LinearActuator/Position/Notify/Number.
  - **READ response**: The peripheral sends a response on the LinearActuator/Position/Notify channel with payload `1` if the peripheral is sending position update notifications with notification interval in units of number of iterations of the peripheral's event loop, `2` if the peripheral is sending position update notifications with notification interval in units of milliseconds, and `0` if the peripheral is not sending position update notifications.

.. _linearactuator_position:
.. uml:: linearactuator_position.uml
   :align: center
   :caption: : Examples of commands and responses associated with the LinearActuator/Position channel.

LinearActuator/SmoothedPosition
-------------------------------

- **Child channels**:

  - LinearActuator/SmoothedPosition/SnapMultiplier
  - LinearActuator/SmoothedPosition/RangeLow
  - LinearActuator/SmoothedPosition/RangeHigh
  - LinearActuator/SmoothedPosition/ActivityThreshold
  - LinearActuator/SmoothedPosition/Notify (child channels are the same as for LinearActuator/Position/Notify)

- **Channel names**:

  - LinearActuator/SmoothedPosition: `_s`

    - LinearActuator/SmoothedPosition/SnapMultiplier: `_ss`
    - LinearActuator/SmoothedPosition/RangeLow: `_sl`
    - LinearActuator/SmoothedPosition/RangeHigh: `_sh`
    - LinearActuator/SmoothedPosition/ActivityThreshold: `_st`
    - LinearActuator/SmoothedPosition/Notify: `_sn` (child channel names are the same as for LinearActuator/Position/Notify, except with `_s` instead of `_p`)

- **Description**: These commands relate to tracking of the (smoothed values from the) position sensor in the linear actuator.

  - LinearActuator/SmoothedPosition represents the smoothed values of the position sensor. Smoothing is done by an exponentially weighted moving average, with special case handling for detecting when a position is constant, as described in [Clarke2016]_.

    - LinearActuator/SmoothedPosition/SnapMultiplier specifies how responsive the smoothed position will be to changes in the raw position. This corresponds to the alpha coefficient for exponentially weighted moving averages.
    - LinearActuator/SmoothedPosition/RangeLow and LinearActuator/SmoothedPosition/RangeHigh specify the minimum and maximum, respectively, allowed values for the smoothed position. Setting these values correctly improves the accuracy of the smoothed position at the limits of the position range.
    - LinearActuator/SmoothedPosition/ActivityThreshold specifies how much the smoothed position must change when the position is considered constant for the position to no longer be considered constant.
    - LinearActuator/SmoothedPosition/Notify behaves the same way as LinearActuator/Position/Notify, but notifies the smoothed values from the position sensor instead of the raw values.

- **Semantics** for LinearActuator/SmoothedPosition/Notify and its child channels are the same as for LinearActuator/Position/Notify

- **Semantics** for child channels besides LinearActuator/SmoothedPosition/Notify: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the variable named by the child channel with the value specified in the payload and sends a READ response with the new value of the variable:

    - Semantics for child channels are not yet defined.

- **Semantics** for LinearActuator/SmoothedPosition channel: READ-only

  - **READ command**: The peripheral simply sends a READ response.
  - **READ response**: The peripheral sends a response on the LinearActuator/Position channel with a payload whose value is the current smoothed position reading from the linear actuator's position sensor.

LinearActuator/Motor
--------------------

- **Child channels**:

  - LinearActuator/Motor/Notify (child channels are the same as for LinearActuator/Position/Notify)

- **Channel names**:

  - LinearActuator/Motor: `_m`

    - LinearActuator/Motor/Notify: `_mn` (child channel names are the same as for LinearActuator/Position/Notify, except with `_m` instead of `_p`)
    - LinearActuator/Motor/StallProtectorTimeout: `_ms`
    - LinearActuator/Motor/TimerTimeout: `_mt`

- **Description**: These commands relate to direct (open-loop) motor duty control and notification of the actuator effort for the motor in the linear actuator. Additionally, commands on child channels relate to conditions for interrupting motor controllers (such as direct motor duty control or feedback control) and stopping actuator effort.

  - LinearActuator/Motor represents the actuator effort (roughly the duty cycle) of the actuator's motor. An actuator effort of `0` corresponds to putting the motor in brake mode, as if the actuator had a high (but finite) coefficient of friction. An actuator effort greater than `0` corresponds to moving the actuator towards higher positions. An actuator effort less than `0` corresponds to moving the actuator towards higher positions. A greater magnitude of actuator effort corresponds to a higher pulse-width modulation duty cycle for the motor, and thus more electric power delivered to the motor. Actuator efforts must be between `-255` and `255`, inclusive.

    - LinearActuator/Motor/Notify behaves the same way as LinearActuator/Position/Notify, but notifies the actuator efforts of the motor instead of the raw position values.

- **Semantics** for LinearActuator/Motor/Notify and its child channels are the same as for LinearActuator/Position/Notify

- **Semantics** for child channels besides LinearActuator/SmoothedPosition/Notify: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the parameter named by the child channel with the value specified in the payload and sends a READ response with the new value of the parameter:

    - LinearActuator/Motor/StallProtectorTimeout specifies how long the motor should run without any changes to the smoothed position (on the LinearActuator/SmoothedPosition channel) before the actuator concludes that the motor has stalled. When the motor has stalled, the actuator interrupts any running motor controller (such as direct motor duty control initiated by LinearActuator/Motor with a non-zero actuator effort or feedback control initiated by LinearActuator/FeedbackController) and sets the motor duty to zero; the peripheral responses triggered by this interruption of the direct motor duty controller are discussed below.

  - **READ response**: The peripheral sends a response whose payload is the value for the motor control parameter named by the (child) channel.

- **Semantics** for LinearActuator/Motor channel: READ/WRITE+Action

  - **WRITE+READ+Actions command**: If the linear actuator was previously in another control mode, such as feedback control mode, it interrupts that control mode and changes the mode to direct motor duty control mode. The peripheral clamps the payload's value to be between `-255` and `255`, inclusive, and sets the result to be the actuator effort (namely, motor direction and PWM duty cycle) for the linear actuator's motor. Then the peripheral sends a READ response for LinearActuator/Motor. Then the peripheral sends a READ response for LinearActuator; if the actuator effort is `0`, the READ response will have payload `0` to indicate that the actuator is operating in direct motor duty control mode with a null duty; otherwise, the READ response will have payload `1` to indiate that the actuator is operating in direct motor duty control mode with nonzero duty. If/when the actuator interrupts the direct motor duty controller, the peripheral will send a response on the LinearActuator/Motor channel, then a response on the LinearActuator/Position channel, and finally a response on the LinearActuator channel.
  - **READ response**: The peripheral sends a response on the LinearActuator/Motor channel with a payload whose value is the current actuator effort of the linear actuator's motor.

.. _linearactuator_motor:
.. uml:: linearactuator_motor.uml
   :align: center
   :caption: : Examples of commands and responses associated with the LinearActuator/Motor channel.

References
----------

.. [Clarke2016] Blog post describing algorithm: `Writing a better noise-reduction algorithm for Arduino <http://damienclarke.me/code/posts/writing-a-better-noise-reducing-analogread>`_; Arduino library on `Github <https://github.com/dxinteractive/ResponsiveAnalogRead>`_

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
  - **READ response**: The peripheral sends a response on the LinearActuator channel with payload `1` if the actuator is operating in direct motor duty control mode with a nonzero duty, `2` if the actuator is operating in position feedback control mode, `0` if the actuator is operating in direct motor duty control mode with a null (zero) duty, `-1` if the actuator's controller has stopped from a motor stall, `-2` if the actuator's controller has stopped from convergence to a feedback control target, and `-3` if the actuator's controller has stopped from a timer timeout. Negative payloads correspond to stopped actuator states where the controller has stopped running, while positive payloads correspond to moving actuator states where the controller is still running, and null (zero) payload corresponds to the stopped actuator state where the controller was initially instructed to stop the actuator.

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
    - In either case, if LinearActuator/Position/ChangeOnly is enabled, the peripheral will not send position update notifications when the position has not changed, which will increase the notification interval above *n*.

  - LinearActuator/Position/Notify/ChangeOnly specifies whether the peripheral will avoid sending position update notifications when the position hasn't changed, to reduce the number of messages sent from the peripheral to the host.
  - LinearActuator/Position/Notify/Number specifies the number of position update notifications the peripheral will send, before it stops sending position update notifications.

- **Semantics** for child channels: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the variable named by the child channel with the value specified in the payload and sends a READ response with the new value of the variable:

    - LinearActuator/Position/Notify/Interval: the payload's value must be a positive number for the variable to be updated with it; otherwise, the variable will remain at its previous value.
    - LinearActuator/Position/Notify/ChangeOnly: if the payload is `1`, the peripheral will not send position update notifications when the position does not change. If the payoad is `0`, the peripheral will send position update notifications regardless of whether the position has changed. Otherwise, the mode will not change from its previous value.
    - LinearActuator/Position/Notify/Number: if the payload's value is negative, then the peripheral will send position notification updates forever (at least until a LinearActuator/Position/Notify command is sent instructing the peripheral to stop sending position updates). If the payload's value is nonnegative, then the peripheral will send that number of position update notifications before the peripheral stops sending position update notifications.

  - **READ response**: The peripheral sends a response whose payload is the value for the position update notification parameter named by the (child) channel.

- **Semantics** for LinearActuator/Position/Notify channel: READ/WRITE+Actions

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
  - LinearActuator/Motor/StallProtectorTimeout
  - LinearActuator/Motor/TimerTimeout
  - LinearActuator/Motor/MotorPolarity

- **Channel names**:

  - LinearActuator/Motor: `_m`

    - LinearActuator/Motor/Notify: `_mn` (child channel names are the same as for LinearActuator/Position/Notify, except with `_m` instead of `_p`)
    - LinearActuator/Motor/StallProtectorTimeout: `_ms`
    - LinearActuator/Motor/TimerTimeout: `_mt`
    - LinearActuator/Motor/MotorPolarity: `_mp`

- **Description**: These commands relate to direct (open-loop) motor duty control and notification of the actuator effort for the motor in the linear actuator. Additionally, commands on child channels relate to conditions for interrupting motor controllers (such as direct motor duty control or feedback control) and stopping actuator effort.

  - LinearActuator/Motor represents the actuator effort (roughly the duty cycle) of the actuator's motor. An actuator effort of `0` corresponds to putting the motor in brake mode, as if the actuator had a high (but finite) coefficient of friction. An actuator effort greater than `0` corresponds to moving the actuator towards higher positions. An actuator effort less than `0` corresponds to moving the actuator towards lower positions. A greater magnitude of actuator effort corresponds to a higher pulse-width modulation duty cycle for the motor, and thus more electric power delivered to the motor. Actuator efforts must be between `-255` and `255`, inclusive.

    - LinearActuator/Motor/Notify behaves the same way as LinearActuator/Position/Notify, but notifies the actuator efforts of the motor instead of the raw position values.
    - LinearActuator/Motor/StallProtectorTimeout specifies how long the motor should run without any changes to the smoothed position (on the LinearActuator/SmoothedPosition channel) before the actuator concludes that the motor has stalled. When the motor has stalled, the actuator interrupts any running motor controller (such as direct motor duty control initiated by LinearActuator/Motor with a non-zero actuator effort or feedback control initiated by LinearActuator/FeedbackController) and sets the motor duty to zero; the peripheral responses triggered by this interruption of the direct motor duty controller are discussed below.
    - LinearActuator/Motor/TimerTimeout specifies the maximum amount of time the motor should run before the actuator stops the motor. When the actuator stops the motor, it interrupts any running motor controller (such as direct motor duty control initiated by LinearActuator/Motor with a non-zero actuator effort or feedback control initiated by LinearActuator/FeedbackController) and sets the motor duty to zero; the peripheral responses triggered by this interruption of the direct motor duty controller are discussed below. Note that the controller may be interrupted before the full timer duration has elapsed, for example if the stall protector interrupts control first.
    - LinearActuator/Motor/Polarity specifies the polarity of the motor, namely whether the polarity should be flipped in software as if the wires for the motor were physically swapped.

- **Semantics** for LinearActuator/Motor/Notify and its child channels are the same as for LinearActuator/Position/Notify

- **Semantics** for child channels besides LinearActuator/SmoothedPosition/Notify: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the parameter named by the child channel with the value specified in the payload and sends a READ response with the new value of the parameter:

    - LinearActuator/Motor/StallProtectorTimeout: the payload's value must be nonnegative for the variable to be updated with it; otherwise, the variable will remain at its previous value. A value of `0` disables stall protection, while a positive value sets the timeout for stall protection.
    - LinearActuator/Motor/TimerTimeout: the payload's value must be nonnegative for the variable to be updated with it; otherwise, the variable will remain at its previous value. A value of `0` disables the timer, while a positive value sets the timeout for the timer.
    - LinearActuator/Motor/Polarity: the payload's value must be either `1` or `-1` for the variable to be updated with it; otherwise, the variable will remain at its previous value. If the payload is `1`, the motor's polarity is not flipped; if the payload is `-1`, the motor's polarity is flipped.

  - **READ response**: The peripheral sends a response whose payload is the value for the motor control parameter named by the (child) channel.

- **Semantics** for LinearActuator/Motor channel: READ/WRITE+Actions

  - **WRITE+READ+Actions command**: If the linear actuator was previously in another control mode, such as feedback control mode, it interrupts that control mode and changes the mode to direct motor duty control mode. The peripheral clamps the payload's value to be between `-255` and `255`, inclusive, and sets the result to be the actuator effort (namely, motor direction and PWM duty cycle) for the linear actuator's motor. Then the peripheral sends a READ response for LinearActuator/Motor. Then the peripheral sends a READ response for LinearActuator; if the actuator effort is `0`, the READ response will have payload `0` to indicate that the actuator is operating in direct motor duty control mode with a null duty; otherwise, the READ response will have payload `1` to indiate that the actuator is operating in direct motor duty control mode with nonzero duty. If/when the actuator interrupts the direct motor duty controller, the peripheral will send a response on the LinearActuator/Motor channel, then a response on the LinearActuator/Position channel, and finally a response on the LinearActuator channel.
  - **READ response**: The peripheral sends a response on the LinearActuator/Motor channel with a payload whose value is the current actuator effort of the linear actuator's motor.

.. _linearactuator_motor:
.. uml:: linearactuator_motor.uml
   :align: center
   :caption: : Examples of commands and responses associated with the LinearActuator/Motor channel.

LinearActuator/FeedbackController
---------------------------------

- **Child channels**:

  - LinearActuator/FeedbackController/Limits (its child channels are documented below)
  - LinearActuator/FeedbackController/PID (its child channels are documented below)
  - LinearActuator/FeedbackController/ConvergenceTimeout

- **Channel names**:

  - LinearActuator/FeedbackController: `_f`

    - LinearActuator/FeedbackController/Limits: `_fl` (names of its child channels are documented below)
    - LinearActuator/FeedbackController/PID: `_fp` (names of its child channels are documented below)
    - LinearActuator/FeedbackController/ConvergenceTimeout: `_fc`

- **Description**: These commands relate to closed-loop position feedback control of the actuator.

  - LinearActuator/FeedbackController is the target position (the setpoint) for position feedback control. The value should be within the range specified by LinearActuator/FeedbackController/Limits/Position/Low and LinearActuator/FeedbackController/Limits/Position/High.

    - LinearActuator/FeedbackController/Limits is the root of a tree of parameters specifying position and motor duty limits.
    - LinearActuator/FeedbackController/PID is the root of a collection of parameters specifying PID controller parameters.
    - LinearActuator/FeedbackController/ConvergenceTimeout specifies how long the controller should run the motor at null (zero) duty cycle (on the LinearActuator/Motor channel) before the controller concludes that the raw position (from LinearActuator/Position) has converged to the target position. When convergence is reached, the controller stops; the resulting peripheral responses are discussed below. Note that the controller may be interrupted (such as by stall protection timeout or a timer timeout) before convegence is reached; the resulting peripheral responses are also discussed below.

- **Semantics** for child channels of LinearActuator/FeedbackController/Limits documented below.
- **Semantics** for child channels of LinearActuator/FeedbackController/PID documented below.
- **Semantics** for the child channel LinearActuator/FeedbackController/ConvergenceTimeout: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the parameter named by the child channel with the value specified in the payload and sends a READ response with the new value of the parameter:

    - LinearActuator/FeedbackController/ConvergenceTimeout: the payload's value must be nonnegative for the variable to be updated with it; otherwise, the variable will remain at its previous value. A value of `0` disables convergence detection (so that the controller will continue running even if the position has converged), while a positive value sets the timeout for convergence detection. Disabling convegence detection functionality allows the actuator to correct any disturbances which may occur after convergence is reached, but it also leaves the actuator vulnerable to moving to account for sensor noise which doesn't constitute a true disturbance, which can produce undesired/spurious actuator motions.

  - **READ response**: The peripheral sends a response whose payload is the value for the feedback control parameter named by the (child) channel.

- **Semantics** for LinearActuator/FeedbackController channel: READ/WRITE+Actions

  - **WRITE+READ+Actions command**: If the linear actuator was previously in another control mode, such as direct duty control mode, it interrupts that control mode and changes the mode to feedback control mode. The peripheral clamps the payload's value to be between the values specified by LinearActuator/FeedbackController/Limits/Position/Low and LinearActuator/FeedbackController/Limits/Position/High, inclusive, and sets the result to be the setpoint (namely, target position) for the controller. Then the peripheral sends a READ response for LinearActuator/FeedbackController. Then the peripheral sends a READ response for LinearActuator, with payload `2` to indicate that the actuator is operating in feedback control mode. If/when the actuator stops or interrupts the feedback controller, the peripheral will send a response on the LinearActuator/Position channel, then a response on the LinearActuator/FeedbackController channel, and finally a response on the LinearActuator channel.
  - **READ response**: The peripheral sends a response on the LinearActuator/FeedbackController channel with a payload whose value is the current target position (setpoint) of the feedback controller.

LinearActuator/FeedbackController/Limits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Child channels**:

  - LinearActuator/FeedbackController/Limits/Position

    - LinearActuator/FeedbackController/Limits/Position/Low
    - LinearActuator/FeedbackController/Limits/Position/High

  - LinearActuator/FeedbackController/Limits/Motor

    - LinearActuator/FeedbackController/Limits/Motor/Forwards

      - LinearActuator/FeedbackController/Limits/Motor/Forwards/Low
      - LinearActuator/FeedbackController/Limits/Motor/Forwards/High

    - LinearActuator/FeedbackController/Limits/Motor/Backwards

      - LinearActuator/FeedbackController/Limits/Motor/Backwards/Low
      - LinearActuator/FeedbackController/Limits/Motor/Backwards/High

- **Channel names**:

  - LinearActuator/FeedbackController/Limits: `_fl`

    - LinearActuator/FeedbackController/Limits/Position: `_flp`

      - LinearActuator/FeedbackController/Limits/Position/Low: `_flpl`
      - LinearActuator/FeedbackController/Limits/Position/High: `_flph`

    - LinearActuator/FeedbackController/Limits/Motor: `_flm`

      - LinearActuator/FeedbackController/Limits/Motor/Forwards: `_flmf`

        - LinearActuator/FeedbackController/Limits/Motor/Forwards/Low: `_flmfl`
        - LinearActuator/FeedbackController/Limits/Motor/Forwards/High: `_flmfh`

      - LinearActuator/FeedbackController/Limits/Motor/Backwards: `_flmb`

        - LinearActuator/FeedbackController/Limits/Motor/Backwards/Low: `_flmbl`
        - LinearActuator/FeedbackController/Limits/Motor/Backwards/High: `_flmbh`

- **Description**: These commands specify input/output limit parameters for closed-loop position feedback control of the actuator.

  - LinearActuator/FeedbackController/Limits is the root of a tree of parameters specifying position and motor duty limits.

    - LinearActuator/FeedbackController/Limits/Position is the root of a tree of parameters specifying position limits.

      - LinearActuator/FeedbackController/Limits/Position/Low specifies the minimum allowed position for the PID controller to move to.

      - LinearActuator/FeedbackController/Limits/Position/High specifies the maximum allowed position for the PID controller to move to.

    - LinearActuator/FeedbackController/Limits/Motor is the root of a tree of parameters specifying motor duty limits.

      - LinearActuator/FeedbackController/Limits/Motor/Forwards is the root of a tree of parameters specifying actuator effort limits for when the motor moves forwards (towards higher positions).

        - LinearActuator/FeedbackController/Limits/Motor/Forwards/Low specifies the minimum allowed actuator effort (positive signed duty cycle) for the motor to run forwards at; when the motor runs forwards, actuator efforts below this are set to `0` to brake the motor.
        - LinearActuator/FeedbackController/Limits/Motor/Forwards/High specifies the maximum allowed actuator effort (positive signed duty cycle) for the motor to run forwards at; when the motor runs forwards, actuator efforts above this are clamped to the value specified here.

      - LinearActuator/FeedbackController/Limits/Motor/Backwards is the root of a tree of parameters specifying actuator effort limits for when the motor moves backwards (towards lower positions).

        - LinearActuator/FeedbackController/Limits/Motor/Backwards/Low specifies the minimum allowed actuator effort (negative signed duty cycle) for the motor to run backwards at; this corresponds to the minimum allowed magnitude of a negative duty cycle, but combined with a negative sign. When the motor runs backwards, actuator efforts above this are set to `0` to brake the motor.
        - LinearActuator/FeedbackController/Limits/Motor/Backwards/High specifies the maximum allowed actuator effort (negative sigined duty cycle) for the motor to run backwards at; this corresponds to the maximum allowed magnitude of a negative duty cycle, but combined with a negative sign. When the motor runs backwards, actuator efforts below this are clamped to the value specified here.

- **Semantics** for child channels: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the parameter named by the child channel with the value specified in the payload and sends a READ response with the new value of the parameter:

    - LinearActuator/FeedbackController/Limits/Position/Low: the payload's value must be less than or equal to the value of the variable corresponding to LinearActuator/FeedbackController/Limits/Position/High for the variable to be updated with it; otherwise, the variable will remain at its previous value.
    - LinearActuator/FeedbackController/Limits/Position/High: the payload's value must be greater than or equal to the value of the variable corresponding to LinearActuator/FeedbackController/Limits/Position/Low for the variable to be updated with it; otherwise, the variable will remain at its previous value.
    - LinearActuator/FeedbackController/Limits/Motor/Forwards/Low: the payload's numerical value must be less than or equal to the numerical value of the variable corresponding to LinearActuator/FeedbackController/Limits/Motor/Forwards/High, and greater than or equal to the numerical value of the variable corresponding to LinearActuator/FeedbackController/Limits/Motor/Backwards/Low, for the variable to be updated with it; otherwise, the variable will remain at its previous value. Generally, this numerical value should be nonnegative, as positive numerical values correspond to forwards movement of the actuator.
    - LinearActuator/FeedbackController/Limits/Motor/Forwards/High: the payload's numerical value must be greater than or equal to the numerical value of the variable corresponding to LinearActuator/FeedbackController/Limits/Motor/Forwards/Low, and less than or equal to 255, for the variable to be updated with it; otherwise, the variable will remain at its previous value. Generally, this value should be nonnegative, as positive numerical values correspond to forwards movement of the actuator.
    - LinearActuator/FeedbackController/Limits/Motor/Backwards/Low: the payload's numerical value must be greater than or equal to the numerical value of the variable corresponding to LinearActuator/FeedbackController/Limits/Motor/Backwards/High, and less than or equal to the numerical value of the variable corresponding to LinearActuator/FeedbackController/Limits/Motor/Forwards/Low, for the variable to be updated with it; otherwise, the variable will remain at its previous value. Generally, this value should be negative, as negative numerical values correspond to backwards movement of the actuator.
    - LinearActuator/FeedbackController/Limits/Motor/Backwards/High: the payload's numerical value must be less than or equal to the numerical value of the variable corresponding to LinearActuator/FeedbackController/Limits/Motor/Backwards/Low, and greater than or equal to -255, for the variable to be updated with it; otherwise, the variable will remain at its previous value. Generally, this value should be negative, as negative numerical values correspond to backwards movement of the actuator.

  - **READ response**: The peripheral sends a response whose payload is the value for the feedback control parameter named by the (child) channel.

LinearActuator/FeedbackController/PID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Child channels**:

  - LinearActuator/FeedbackController/PID

    - LinearActuator/FeedbackController/PID/Kp
    - LinearActuator/FeedbackController/PID/Kd
    - LinearActuator/FeedbackController/PID/Ki
    - LinearActuator/FeedbackController/PID/SampleInterval

- **Channel names**:

  - LinearActuator/FeedbackController/PID: `_fp`

    - LinearActuator/FeedbackController/PID/Kp: `_fpp`
    - LinearActuator/FeedbackController/PID/Kd: `_fpd`
    - LinearActuator/FeedbackController/PID/Ki: `_fpi`
    - LinearActuator/FeedbackController/PID/SampleInterval: `_fps`

- **Description**: These commands specify PID controller parameters for closed-loop position feedback control of the actuator.

  - LinearActuator/FeedbackController/PID is the root of a collection of parameters specifying PID controller parameters.

    - LinearActuator/FeedbackController/PID/Kp is the proportional gain of the PID controller.
    - LinearActuator/FeedbackController/PID/Kd is the derivative gain of the PID controller.
    - LinearActuator/FeedbackController/PID/Ki is the integral gain of the PID controller.
    - LinearActuator/FeedbackController/PID/SampleInterval is the duration of the interval (in milliseconds) between updates of the PID controller's output.

- **Semantics** for child channels: READ/WRITE

  - **WRITE+READ command**: The peripheral updates the parameter named by the child channel with the value specified in the payload and sends a READ response with the new value of the parameter:

    - LinearActuator/FeedbackController/PID/Kp: the payload's value must be a positive number for it to be preserved when the variable is updated with it; otherwise, the variable's value will be a different, corrected value. The gain is a fixed-point representation of a real number, namely the real number multiplied by `100` and then rounded to the nearest integer. Thus, setting Kp to `0.1` requires sending a LinearActuator/FeedbackController/PID/Kp(10) command. The response is given in the same fixed-point representation.
    - LinearActuator/FeedbackController/PID/Kd: the payload's value must be a positive number for it to be preserved when the variable is updated with it; otherwise, the variable's value will be a different, corrected value. The gain is a fixed-point representation of a real number, namely the real number multiplied by `100` and then rounded to the nearest integer. Thus, setting Kd to `0.1` requires sending a LinearActuator/FeedbackController/PID/Kd(10) command. The response is given in the same fixed-point representation.
    - LinearActuator/FeedbackController/PID/Ki: the payload's value must be a positive number for it to be preserved when the variable is updated with it; otherwise, the variable's value will be a different, corrected value. The gain is a fixed-point representation of a real number, namely the real number multiplied by `100` and then rounded to the nearest integer. Thus, setting Ki to `0.1` requires sending a LinearActuator/FeedbackController/PID/Ki(10) command. The response is given in the same fixed-point representation.
    - LinearActuator/FeedbackController/PID/SampleInterval: the payload's value must be a positive number for the variable to be updated with it; otherwise, the variable will remain at its previous value.

  - **READ response**: The peripheral sends a response whose payload is the value for the feedback control parameter named by the (child) channel.

.. _linearactuator_feedbackcontroller:
.. uml:: linearactuator_feedbackcontroller.uml
   :align: center
   :caption: : Examples of commands and responses associated with the LinearActuator/FeedbackController channel.

References
----------

.. [Clarke2016] Blog post describing algorithm: `Writing a better noise-reduction algorithm for Arduino <http://damienclarke.me/code/posts/writing-a-better-noise-reducing-analogread>`_; Arduino library on `Github <https://github.com/dxinteractive/ResponsiveAnalogRead>`_

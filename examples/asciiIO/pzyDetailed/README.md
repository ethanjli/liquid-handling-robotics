# pzyDetailed

This Arduino sketch implements position control of the pipettor axis, the z axis, and the y axis. It behaves the same way as the pzyRobot sketch, except it avoids using high-level macros provided by `StandardLiquidHandlingRobot.h` which simplify sketch code; this sketch shows all the details of the classes provided by the library in their full glory. The Arduino can be controlled over a Serial connection (such as from the Arduino's Serial Monitor) with human-readable command and response messages.

## Hardware

Laser-cut pieces should be cut on 1/8 inch acrylic. Note that kerf adjustments are specific to the laser cutter in the Camarillo lab and may need to be adjusted for other laser cutters.

## Wiring

This sketch is configured to drive the pipettor axis motor on port M1, the z axis motor on port M2, and the y axis motor on port M3 of the Adafruit Motor Shield. Instructions for the wiring of the pipettor and z axes are available [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/pipettor/electrical/index.html) and [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/verticalpositioner/electrical/index.html), respectively. If the motor for some axis is trying to push past the end of the axis in either direction, you may need to switch the wires for that motor. A future version of this library will provide test sketches to help you determine whether you need to switch wires for these motors.


## Library Dependencies

To compile this sketch, the following libraries must be installed from the Arduino IDE's Library Manager:

* [Adafruit Motor Shield V2 Library](https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library)
* [elapsedMillis](https://github.com/pfeerick/elapsedMillis/wiki)
* [ArduinoLog](https://github.com/thijse/Arduino-Log/)
* [Arduino PID Library](http://playground.arduino.cc/Code/PIDLibrary)
* [3D-Magnetic-Sensor-2GO](https://github.com/Infineon/TLV493D-A1B6-3DMagnetic-Sensor)
* [ResponsiveAnalogRead](https://github.com/dxinteractive/ResponsiveAnalogRead)
* [Linear Position Control](https://github.com/ethanjli/linear-position-control)
* [Liquid Handling Robotics](https://github.com/ethanjli/liquid-handling-robotics)

## Control

Position control is done by PID control. Note that control parameters are not perfectly tuned and will vary across different builds of the pipetting subsystem.

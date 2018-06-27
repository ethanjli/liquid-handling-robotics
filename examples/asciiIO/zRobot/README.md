# zRobot

This Arduino sketch implements position control of the z axis. The Arduino can be controlled over a Serial connection (such as from the Arduino's Serial Monitor) with human-readable command and response messages.

## Hardware

Laser-cut pieces should be cut on 1/8 inch acrylic. Note that kerf adjustments are specific to the laser cutter in the Camarillo lab and may need to be adjusted for other laser cutters.

## Wiring

This sketch is configured to drive the pipettor axis motor on port M1. Instructions for the wiring of the z axis are available [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/verticalpositioner/electrical/index.html). If the motor for some axis is trying to push past the end of the axis in either direction, you may need to switch the wires for that motor. A future version of this library will provide test sketches to help you determine whether you need to switch wires for these motors.

## Library Dependencies

To compile this sketch, the following libraries must be installed from the Arduino IDE's Library Manager:

* [Adafruit Motor Shield V2 Library](https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library)
* [elapsedMillis](https://github.com/pfeerick/elapsedMillis/wiki)
* [ArduinoLog](https://github.com/thijse/Arduino-Log/)
* [Arduino PID Library](http://playground.arduino.cc/Code/PIDLibrary)
* [ResponsiveAnalogRead](https://github.com/dxinteractive/ResponsiveAnalogRead)
* [Linear Position Control](https://github.com/ethanjli/linear-position-control)
* [Liquid Handling Robotics](https://github.com/ethanjli/liquid-handling-robotics)

## Control

Position control is done by PID control. Note that control parameters are not perfectly tuned and will vary across different builds of the pipetting subsystem.
# pzyxRobot

This Arduino sketch implements position control of the pipettor axis, the z axis, the y axis, and the x axis. The Arduino must be controlled over a Serial Firmata connection (such as from Snap4Arduino).

## Electronics

Currently, memory limitations require that this sketch be used with an Arduino Mega.

## Hardware

Laser-cut pieces should be cut on 1/8 inch acrylic. Note that kerf adjustments are specific to the laser cutter in the Camarillo lab and may need to be adjusted for other laser cutters.

## Wiring

This sketch is configured to drive the pipettor axis motor on port M1 and the z axis motor on port M2. Instructions for the wiring of the pipettor and z axes are available [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/pipettor/electrical/index.html) and [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/verticalpositioner/electrical/index.html), respectively. If the motor for some axis is trying to push past the end of the axis in either direction, you may need to switch the wires for that motor. A future version of this library will provide test sketches to help you determine whether you need to switch wires for these motors.

## Library Dependencies

To compile this sketch, the following libraries must be installed from the Arduino IDE's Library Manager:

* [Adafruit Motor Shield V2 Library](https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library)
* [elapsedMillis](https://github.com/pfeerick/elapsedMillis/wiki)
* [ArduinoLog](https://github.com/thijse/Arduino-Log/)
* [Arduino PID Library](http://playground.arduino.cc/Code/PIDLibrary)
* [ResponsiveAnalogRead](https://github.com/dxinteractive/ResponsiveAnalogRead)
* [Linear Position Control](https://github.com/ethanjli/linear-position-control)
* [Liquid Handling Robotics](https://github.com/ethanjli/liquid-handling-robotics)
* [Configurable Firmata](https://github.com/firmata/ConfigurableFirmata)

Additionally, the following Arduino libraries must be installed manually:

* [TLV493D-A1B6-3DMagnetic-Sensor](https://github.com/ethanjli/TLV493D-A1B6-3DMagnetic-Sensor)

## Control

Position control is done by PID control. Note that control parameters are not perfectly tuned and will vary across different builds of the pipetting subsystem.

# pipettor

This Arduino sketch implements position control of the pipettor module and exposes a serial interface for specifying position setpoints.

## Hardware

This sketch controls the pipettor module subsystem. Laser-cut pieces should be cut on 1/8 inch acrylic. Note that kerf adjustments are specific to the laser cutter in the Camarillo lab and may need to be adjusted for other laser cutters. The complete Bill of Materials for all non-acrylic components required to assemble this subsystem can be found [here](https://docs.google.com/spreadsheets/d/13kbot_s2HfTaFTPpONHiX8-gXCsIVLI1q1TLE1A9vvY/edit?usp=drive_web).

## Wiring

This sketch is configured to drive the motor on port M1 of the Adafruit Motor Shield. The red wire for the motor is assumed to be in the terminal block hole closer to GND on the Motor Shield than the blue wire for the motor. The red wire for the motor should be closer to the slide potentiometer than the blue wire. If the motor is trying to push past the end of the pipettor in either direction, you may need to switch the wires. A future iteration of the embedded software hardware abstraction layer will automatically detect motor polarity and swap motor directions when necessary.

The sketch uses pin A0 for output line of the slide potentiometer (pin 2 on the potentiometer); pin 1 of the potentiometer should connect to GND, while pin 3 of the potentiometer should connect to 5V. Pin 3 of the potentiometer should be closer to the syringe.

## Library Dependencies

To compile this sketch, the following libraries must be installed:

* Adafruit Motor Shield V2 Library
* Arduino Log
* Arduino PID Library
* elapsedMillis

You can use the Arduino IDE to install these libraries from the zip files in the `dependencies` directory.

Additionally, you must download the [linear-position-control repository](https://github.com/ethanjli/linear-position-control) and copy the `library` directory from that directory into your Arduino libraries folder (and you may want to rename it to something like `linear-position-control`). In the future, we'll make this process easier.

Additionally, you must copy the `lhr-control` directory into your Arduino libraries folder.

## Serial Protocol

This sketch supports easy usage over the Arduino Serial Monitor. More user-friendly control can be used with the lhrhost package in this repository.

When the Arduino is first connected to a computer as a client over USB, it repeatedly sends the handshake character `~` until it receives a response (any response ending in a newline `\n` will do) from the host. The pipettor then moves to the highest possible position and, when it has initially reached and stabilized at that position, reports the current position over serial in the format `<pc>[number]` (as its own line), for example `<pc>[8]`. At any time, the user can send a message in the format `<pt>[number]` to command the pipettor to move to the desired position. The pipettor will then move to the nearest position within the allowed range and, when it has initially reached and stabilized at that position, report its current position over serial. The Arduino will ignore any messages not of the format `<pc>[number]`.

## Control

Position control is done by PID control. Note that control parameters are tuned for operation with a monoject tuberculin syringe and may vary across motors and syringes. Control parameters have not yet been perfectly tuned.

# verticalPositioner

This Arduino sketch implements position control of the pipettor and vertical positioner modules (which together are called the *pipetting subsystem*) and exposes a serial interface for specifying position setpoints for each module.

## Hardware

This sketch controls the pipetting subsystem. Laser-cut pieces should be cut on 1/8 inch acrylic. Note that kerf adjustments are specific to the laser cutter in the Camarillo lab and may need to be adjusted for other laser cutters. The complete Bill of Materials for all non-acrylic components required to assemble this subsystem can be found [here](https://docs.google.com/spreadsheets/d/15u-hYOI23gvRaB4oQE1RWmyJhvHIh52ai5TX3SBh1B4/edit#gid=0).

## Wiring

This sketch is configured to drive the pipettor's motor on port M1 and the vertical positioner's motor on port M2 of the Adafruit Motor Shield. Instructions for the wiring of the pipettor module and the vertical positioner module are available [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/pipettor/electrical/index.html) and [here](http://liquid-handling-robotics.readthedocs.io/en/latest/assembly/verticalpositioner/electrical/index.html), respectively. If the motor for some module is trying to push past the end of the pipettor in either direction, you may need to switch the wires for that motor. A future iteration of the embedded software hardware abstraction layer will automatically detect motor polarity and swap motor directions when necessary.

## Library Dependencies

To compile this sketch, the following libraries must be installed:

* Adafruit Motor Shield V2 Library
* Arduino Log
* Arduino PID Library
* elapsedMillis

You can use the Arduino IDE to install these libraries from the zip files in the `dependencies` directory.

Additionally, you must download the [linear-position-control repository](https://github.com/ethanjli/linear-position-control) and copy the `library` directory from that directory into your Arduino libraries folder (and you may want to rename it to something like `linear-position-control`). In the future, we'll make this process easier.

Additionally, you must copy the `lhr-control` directory from this repository into your Arduino libraries folder. Then you can upload this sketch from the Arduino IDE via File -> Examples -> lhr-control -> verticalPositioner.

## Serial Protocol

This sketch supports easy usage over the Arduino Serial Monitor. More user-friendly control can be used with the lhrhost package in this repository.

When the Arduino is first connected to a computer as a client over USB, it repeatedly sends the handshake character `~` until it receives a response (any response ending in a newline `\n` will do) from the host. The pipettor then reports its current position over serial in the format `<pc>[number]` (as its own line), for example `<pc>[8]`. The vertical positioner will also report its current position over serial in the format `<zc>[number]` (as its own line), for example `<zc>[900]`.

To move the pipettor, at any time, the user can send a message in the format `<pt>[number]` to command the pipettor to move to the desired position. The pipettor will then move to the nearest position within the allowed range and, when it has initially reached and stabilized at that position, report its current position over serial as a response with the format `<pc>[number]`. The pipettor module will ignore any messages not of the format `<pt>[number]`. The mnemonics for these commands are **p**ipettor position **c**onverged for **pc** and **p**ipettor position **t**argeting for **pt**.

To move the vertical positioner, at any time, the user can send a message in the format `<zt>[number]` to command the pipettor to move to the desired position. The vertical positioner will then move to the nearest position within the allowed range and, when it has initially reached and stabilized at that position, report its current position over serial as a response with the format `<zc>[number]`. The vertical positioner module will ignore any messages not of the format `<zt>[number]`. The mnemonics for these commands are **z** position **c**onverged for **zc** and **z** position **t**argeting for **zt**.

## Control

Position control is done by PID control. Note that control parameters are not perfectly tuned and will vary across different builds of the pipetting subsystem.

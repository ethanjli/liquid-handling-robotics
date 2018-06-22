# minimalFirmataDetailed

This Arduino sketch only provides minimal Firmata functionality, without control of robot hardware, except it avoids the classes which abstract away the details of ConfigurableFirmata; this sketch shows all the details of ConfigurableFirmata in their full glory, and is in fact essentially a pared-down version of a minimal ConfigurableFirmata sketch as built by [FirmataBuilder](http://firmatabuilder.com/). The Arduino must be controlled over a Serial Firmata connection (such as from Snap4Arduino).

## Library Dependencies

To compile this sketch, the following libraries must be installed from the Arduino IDE's Library Manager:

* [elapsedMillis](https://github.com/pfeerick/elapsedMillis/wiki)
* [ArduinoLog](https://github.com/thijse/Arduino-Log/)
* [Linear Position Control](https://github.com/ethanjli/linear-position-control)
* [Liquid Handling Robotics](https://github.com/ethanjli/liquid-handling-robotics)
* [Configurable Firmata](https://github.com/firmata/ConfigurableFirmata)

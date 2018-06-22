# coreProtocol

This Arduino sketch implements only the basic communication protocol (namely the [Core](https://liquid-handling-robotics.readthedocs.io/en/latest/messages/core.html) and [Board](https://liquid-handling-robotics.readthedocs.io/en/latest/messages/board.html) protocol subsets), without control of robot hardware. The Arduino must be controlled over a Serial Firmata connection (such as from Snap4Arduino).

## Library Dependencies

To compile this sketch, the following libraries must be installed from the Arduino IDE's Library Manager:

* [elapsedMillis](https://github.com/pfeerick/elapsedMillis/wiki)
* [ArduinoLog](https://github.com/thijse/Arduino-Log/)
* [Linear Position Control](https://github.com/ethanjli/linear-position-control)
* [Liquid Handling Robotics](https://github.com/ethanjli/liquid-handling-robotics)
* [Configurable Firmata](https://github.com/firmata/ConfigurableFirmata)

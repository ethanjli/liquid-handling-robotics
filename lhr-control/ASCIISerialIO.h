#ifndef ASCIISerialIO_h
#define ASCIISerialIO_h

#include "Messages.h"

namespace LiquidHandlingRobotics {

namespace ASCIISerial {
  const long kDataRate = 115200;
  const char kHandshakeChar = '~';
}

void waitForHandshake(HardwareSerial& serial = Serial, unsigned long waitDelay = 500);

using SerialMessageSender = MessageSender<HardwareSerial>;
using SerialMessageParser = MessageParser<HardwareSerial>;
using SerialMessager = Messager<HardwareSerial>;

}

#endif


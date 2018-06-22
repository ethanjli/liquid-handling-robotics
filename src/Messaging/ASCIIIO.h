#ifndef LHR_Messaging_ASCIIIO_h
#define LHR_Messaging_ASCIIIO_h

#include "Messages.h"

namespace LiquidHandlingRobotics { namespace Messaging {

namespace ASCIIIO {
  const long kDataRate = 115200;
  const char kHandshakeChar = '~';

  void waitForHandshake(HardwareSerial& serial = Serial, unsigned long waitDelay = 500);
}

using ASCIIMessageSender = MessageSender<HardwareSerial>;
using ASCIIMessageParser = MessageParser<HardwareSerial>;
using ASCIIMessager = Messager<HardwareSerial>;

} }

#include "ASCIIIO.tpp"

#endif


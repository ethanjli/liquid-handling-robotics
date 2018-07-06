#ifndef LHR_Messaging_ASCIIIO_tpp
#define LHR_Messaging_ASCIIIO_tpp

#include <avr/wdt.h>

#include <elapsedMillis.h>

namespace LiquidHandlingRobotics { namespace Messaging {

namespace ASCIIIO {

void waitForHandshake(HardwareSerial &serial, unsigned long waitDelay) {
  elapsedMillis timer;

  // Wait for serial to become ready
  while (!serial) wdt_reset();

  // Print handshake char until input is received
  while (serial.available() < 1) {
    serial.println(kHandshakeChar);
    timer = 0;
    while (timer < waitDelay) wdt_reset();
  }

  // Wait for (and read) input until a newline is received
  while (serial.available() > 0) {
    if (serial.read() == '\n') break;
  }

  // Send a newline response
  serial.println();

  // Wait a bit longer
  timer = 0;
  while (timer < waitDelay) wdt_reset();
}

}

// ASCIIMessageSender

template<>
MessageSender<HardwareSerial>::MessageSender() :
  transport(Serial)
{}

template<>
void MessageSender<HardwareSerial>::setup() {}

template<>
void MessageSender<HardwareSerial>::sendMessageStart() {}

template<>
void MessageSender<HardwareSerial>::sendMessageEnd() {
  transport.write('\n');
}

// ASCIIMessageParser

template<>
MessageParser<HardwareSerial>::MessageParser() :
  MessageParser(Serial)
{}

// ASCIIMessager

template<>
Messager<HardwareSerial>::Messager() :
  sender(Serial), parser(Serial), transport(Serial)
{}

template<>
void Messager<HardwareSerial>::setup() {
  using namespace Messaging::ASCIIIO;

  if (setupCompleted) return;

  transport.begin(kDataRate);

  parser.setup();
  sender.setup();

  setupCompleted = true;
}

template<>
void Messager<HardwareSerial>::establishConnection() {
  using namespace Messaging::ASCIIIO;

  waitForHandshake(transport);
}

} }

#endif


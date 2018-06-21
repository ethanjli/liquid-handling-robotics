#ifndef ASCIISerialIO_tpp
#define ASCIISerialIO_tpp

#include <avr/wdt.h>

#include <elapsedMillis.h>

namespace LiquidHandlingRobotics {

void waitForHandshake(HardwareSerial &serial, unsigned long waitDelay) {
  elapsedMillis timer;

  // Wait for serial to become ready
  while (!serial) wdt_reset();

  // Print handshake char until input is received
  while (serial.available() < 1) {
    serial.println(ASCIISerial::kHandshakeChar);
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

// MessageSender

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

// MessageParser

template<>
MessageParser<HardwareSerial>::MessageParser() :
  transport(Serial)
{}

// Messager

template<>
Messager<HardwareSerial>::Messager() :
  sender(Serial), parser(Serial), transport(Serial)
{}

template<>
void Messager<HardwareSerial>::setup() {
  if (setupCompleted) return;

  transport.begin(ASCIISerial::kDataRate);

  parser.setup();
  sender.setup();

  setupCompleted = true;
}

template<>
void Messager<HardwareSerial>::establishConnection() {
  waitForHandshake(transport);
}

}

#endif


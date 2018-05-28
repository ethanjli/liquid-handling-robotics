#include "ASCIISerialIO.h"

#include <avr/wdt.h>

#include <elapsedMillis.h>

namespace LiquidHandlingRobotics {

void waitForSerialHandshake(char handshakeChar, unsigned long waitDelay) {
  elapsedMillis timer;

  // Wait for Serial to become ready
  while (!Serial) wdt_reset();

  // Print handshake char until input is received
  while (Serial.available() < 1) {
    Serial.println(handshakeChar);
    timer = 0;
    while (timer < waitDelay) wdt_reset();
  }

  // Wait for (and read) input until a newline is received
  while (Serial.available() > 0) {
    if (Serial.read() == '\n') break;
  }

  // Send a newline response
  Serial.println();

  // Wait a bit longer
  timer = 0;
  while (timer < waitDelay) wdt_reset();
}

// MessageSender

template<>
MessageSender<HardwareSerial>::MessageSender() :
  transport(Serial)
{}

// MessageParser

template<>
MessageParser<HardwareSerial>::MessageParser() :
  transport(Serial)
{}

// Messager

template<>
Messager<HardwareSerial>::Messager() :
  sender(Serial), parser(Serial)
{}

}


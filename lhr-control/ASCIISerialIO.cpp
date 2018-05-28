#include "ASCIISerialIO.h"

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

void waitForSerialHandshake(char handshakeChar, unsigned long waitDelay) {
  while (!Serial) {;}
  while (Serial.available() < 1) {
    Serial.println(handshakeChar);
    delay(waitDelay);
  }
  while (Serial.available() > 0) {
    if (Serial.read() == '\n') break;
  }
  Serial.println();
  delay(waitDelay);
}

}


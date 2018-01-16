//#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <Pipettor.h>
#include <ASCIISerialIO.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
MessageParser messageParser;

// Shared Components
LinearPositionControl::Components::Motors motors;

// Subsystems
Pipettor pipettor(messageParser, motors);

void setup() {
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messageParser.setup();
  pipettor.setup();
  waitForSerialHandshake();
}

void loop() {
  messageParser.update();
  pipettor.update();
}

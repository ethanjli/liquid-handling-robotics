//#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
MessageParser messageParser;

// Shared Components
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator pipettor(messageParser, motors, pipettorParams);
AbsoluteLinearActuator verticalPositioner(messageParser, motors, verticalPositionerParams);
CumulativeLinearActuator yPositioner(messageParser, motors, yPositionerParams);

void setup() {
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messageParser.setup();
  pipettor.setup();
  verticalPositioner.setup();
  yPositioner.setup();
  waitForSerialHandshake();
}

void loop() {
  messageParser.update();
  pipettor.update();
  verticalPositioner.update();
  yPositioner.update();
}

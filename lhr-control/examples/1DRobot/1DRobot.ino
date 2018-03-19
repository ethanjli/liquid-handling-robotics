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
LinearPositionControl::CumulativePositionCalibrator yPositionerCalibrator(yPositioner.actuator);

void setup() {
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messageParser.setup();
  pipettor.setup();
  verticalPositioner.setup();
  yPositioner.setup();
  yPositionerCalibrator.setup();
  waitForSerialHandshake();
}

void loop() {
  messageParser.update();
  pipettor.update();
  verticalPositioner.update();
  if (yPositionerCalibrator.state.current() == LinearPositionControl::CumulativePositionCalibrator::State::calibrated) yPositioner.update();
  else yPositionerCalibrator.update();
}

#include <avr/wdt.h>

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
AbsoluteLinearActuator pipettor(messageParser, motors, kPipettorParams);
AbsoluteLinearActuator verticalPositioner(messageParser, motors, kVerticalPositionerParams);
CumulativeLinearActuator yPositioner(messageParser, motors, kYPositionerParams);
LinearPositionControl::CumulativePositionCalibrator yPositionerCalibrator(yPositioner.actuator);

void setup() {
  wdt_disable();
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
  wdt_enable(WDTO_1S);
}

void loop() {
  wdt_reset();
  messageParser.update();
  handleResetCommand(messageParser);
  handleVersionCommand(messageParser);
  handleEchoCommand(messageParser);
  pipettor.update();
  verticalPositioner.update();
  if (yPositionerCalibrator.state.current() == LinearPositionControl::CumulativePositionCalibrator::State::calibrated) yPositioner.update();
  else yPositionerCalibrator.update();
}

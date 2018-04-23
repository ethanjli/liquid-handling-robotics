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
LinearPositionControl::SmoothedCumulativePositionCalibrator yPositionerCalibrator(
  yPositioner.actuator, yPositioner.smoother, kYPositionerCalibrationParams
);

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
  sendAllVersionMessages();
}

void loop() {
  wdt_reset();
  messageParser.update();
  // Standard protocol
  wdt_reset();
  handleResetCommand(messageParser);
  handleVersionCommand(messageParser);
  handleEchoCommand(messageParser);
  handleIOCommand(messageParser);
  // Modules
  wdt_reset();
  pipettor.update();
  wdt_reset();
  verticalPositioner.update();
  wdt_reset();
  if (yPositionerCalibrator.calibrated()) {
    yPositioner.update();
  } else { // initialize positions of z-axis and y-axis
    if (verticalPositioner.actuator.pid.setpoint.current() == 0) {
      // Make the z-axis move up so the syringe doesn't hit anything during y-axis initialization
      verticalPositioner.actuator.pid.setSetpoint(verticalPositioner.actuator.pid.getMaxInput());
      verticalPositioner.actuator.unfreeze();
    } else if (verticalPositioner.converged() || verticalPositioner.stalled()) {
      verticalPositioner.actuator.freeze();
      yPositionerCalibrator.update();
    }
  }
}

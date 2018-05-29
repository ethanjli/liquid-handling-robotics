#include <avr/wdt.h>

#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator<SerialMessager> pipettor(messager, motors, kPipettorParams);
AbsoluteLinearActuator<SerialMessager> verticalPositioner(messager, motors, kVerticalPositionerParams);
CumulativeLinearActuator<SerialMessager> yPositioner(messager, motors, kYPositionerParams);
LinearPositionControl::SmoothedCumulativePositionCalibrator yPositionerCalibrator(
  yPositioner.actuator, yPositioner.smoother, kYPositionerCalibrationParams
);

void setup() {
  wdt_disable();
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messager.setup();
  pipettor.setup();
  verticalPositioner.setup();
  yPositioner.setup();
  yPositionerCalibrator.setup();
  waitForSerialHandshake();
  wdt_enable(WDTO_2S);
  sendAllVersionMessages(messager.sender);
}

void loop() {
  messager.update();
  // Standard protocol
  wdt_reset();
  handleResetCommand(messager);
  handleVersionCommand(messager);
  handleEchoCommand(messager);
  handleIOCommand(messager);
  // Modules
  pipettor.update();
  verticalPositioner.update();
  if (yPositionerCalibrator.calibrated()) {
    yPositioner.update();
  } else { // initialize positions of z-axis and y-axis
    if (verticalPositioner.actuator.pid.setpoint.current() == 0) {
      // Make the z-axis move up so the syringe doesn't hit anything during y-axis initialization
      verticalPositioner.actuator.pid.setSetpoint(verticalPositioner.actuator.pid.getMaxInput());
      verticalPositioner.actuator.unfreeze();
    } else if (verticalPositioner.converged() || verticalPositioner.stalled() || verticalPositioner.stopped()) {
      verticalPositioner.actuator.freeze();
      yPositionerCalibrator.update();
    }
  }
}

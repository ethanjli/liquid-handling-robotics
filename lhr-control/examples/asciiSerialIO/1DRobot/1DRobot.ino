#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
CoreProtocol<SerialMessager> coreProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator<SerialMessager> pipettor(messager, motors, kPipettorParams);
AbsoluteLinearActuator<SerialMessager> verticalPositioner(messager, motors, kVerticalPositionerParams);
CumulativeLinearActuator<SerialMessager> yPositioner(messager, motors, kYPositionerParams);
LinearPositionControl::SmoothedCumulativePositionCalibrator yPositionerCalibrator(
  yPositioner.actuator, yPositioner.smoother, kYPositionerCalibrationParams
);

void setup() {
  coreProtocol.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  pipettor.setup();
  verticalPositioner.setup();
  yPositioner.setup();
  yPositionerCalibrator.setup();
  messager.establishConnection();
  coreProtocol.onConnect();
}

void loop() {
  messager.update();
  coreProtocol.update();
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
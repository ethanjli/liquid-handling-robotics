#define DISABLE_LOGGING

#include <FirmataIO.h>
#include <CoreProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// Firmata communications
FirmataTransport transport;
FirmataMessager messager(transport);
makeFirmataTransportResetCallback(transport);

// Shared components
CoreProtocol<FirmataMessager> coreProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
//AbsoluteLinearActuator<FirmataMessager> pipettor(messager, motors, kPipettorParams);
//AbsoluteLinearActuator<FirmataMessager> verticalPositioner(messager, motors, kVerticalPositionerParams);
CumulativeLinearActuator<FirmataMessager> yPositioner(messager, motors, kYPositionerParams);
LinearPositionControl::SmoothedCumulativePositionCalibrator yPositionerCalibrator(
  yPositioner.actuator, yPositioner.smoother, kYPositionerCalibrationParams
);

void setup()
{
  coreProtocol.setup();
  transport.setup();
  attachFirmataTransportResetCallback(transport);
  messager.setup();
  //pipettor.setup();
  //verticalPositioner.setup();
  yPositioner.setup();
  yPositionerCalibrator.setup();
  messager.establishConnection();
  coreProtocol.onConnect();
}

void loop() {
  transport.update();
  messager.update();
  coreProtocol.update();
  // Modules
  //pipettor.update();
  //verticalPositioner.update();
  if (yPositionerCalibrator.calibrated()) {
    yPositioner.update();
  } else { // initialize positions of z-axis and y-axis
    //if (verticalPositioner.actuator.pid.setpoint.current() == 0) {
      // Make the z-axis move up so the syringe doesn't hit anything during y-axis initialization
      //verticalPositioner.actuator.pid.setSetpoint(verticalPositioner.actuator.pid.getMaxInput());
      //verticalPositioner.actuator.unfreeze();
    //} else if (verticalPositioner.converged() || verticalPositioner.stalled() || verticalPositioner.stopped()) {
      //verticalPositioner.actuator.freeze();
      yPositionerCalibrator.update();
    //}
  }
}

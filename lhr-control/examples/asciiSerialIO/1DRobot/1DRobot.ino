#define DISABLE_LOGGING
#include <ArduinoLog.h>

#define LPC_Components_Motors
#include <LinearPositionControl.h>

#define LHR_Messaging_ASCIIIO
#define LHR_Protocol_Core
//#define LHR_Protocol_Board
#define LHR_Protocol_AbsoluteLinearActuatorAxis
#define LHR_Protocol_CumulativeLinearActuatorAxis
#include <LiquidHandlingRobotics.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// Shared Components
LinearPositionControl::Components::Motors motors;
Messager messager;

// Protocol
Core coreProtocol(messager);
//Board boardProtocol(messager);
AbsoluteLinearActuatorAxis pipettor(messager, motors, kPipettorParams);
AbsoluteLinearActuatorAxis verticalPositioner(messager, motors, kVerticalPositionerParams);
CumulativeLinearActuatorAxis yPositioner(messager, motors, kYPositionerParams);
LinearPositionControl::Control::SmoothedCumulativePositionCalibrator yPositionerCalibrator(
  yPositioner.actuator, yPositioner.smoother, kYPositionerCalibrationParams
);

void updateCommon() {
  messager.update();
  coreProtocol.update();
  //boardProtocol.update();
  pipettor.update();
  verticalPositioner.update();
}

void initializeAxes() {
  // Make the z-axis move up so the syringe doesn't hit anything during y-axis initialization
  verticalPositioner.startDirectMotorDutyControl(255);
  while (!verticalPositioner.state.at(AbsoluteLinearActuatorAxis::State::stallTimeoutStopped)) updateCommon();
  verticalPositioner.startDirectMotorDutyControl(0);
  verticalPositioner.onConnect();

  // Calibrate the y-axis
  while (!yPositionerCalibrator.calibrated()) {
    updateCommon();
    yPositionerCalibrator.update();
  }
  yPositioner.onConnect();
}

void setup() {
  coreProtocol.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  //boardProtocol.setup();
  pipettor.setup();
  verticalPositioner.setup();
  yPositioner.setup();
  yPositionerCalibrator.setup();

  messager.establishConnection();

  coreProtocol.onConnect();
  //boardProtocol.onConnect();
  pipettor.onConnect();
  initializeAxes();
}

void loop() {
  updateCommon();
  yPositioner.update();
}

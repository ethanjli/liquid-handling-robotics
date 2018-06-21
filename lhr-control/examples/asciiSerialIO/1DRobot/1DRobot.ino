#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <AbsoluteLinearPositionControl.h>
#include <CumulativeLinearPositionControl.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
//#include <BoardProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;
using Core = CoreProtocol<SerialMessager>;
//using Board = BoardProtocol<SerialMessager>;
using AbsoluteAxis = AbsoluteLinearActuator<SerialMessager>;
using CumulativeAxis = CumulativeLinearActuator<SerialMessager>;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
Core coreProtocol(messager);
//Board boardProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteAxis pipettor(messager, motors, kPipettorParams);
AbsoluteAxis verticalPositioner(messager, motors, kVerticalPositionerParams);
CumulativeAxis yPositioner(messager, motors, kYPositionerParams);
LinearPositionControl::SmoothedCumulativePositionCalibrator yPositionerCalibrator(
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
  while (!verticalPositioner.state.at(AbsoluteAxis::State::stallTimeoutStopped)) updateCommon();
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

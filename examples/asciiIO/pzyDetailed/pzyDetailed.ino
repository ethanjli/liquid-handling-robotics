#define DISABLE_LOGGING
#include <ArduinoLog.h>

#define LHR_Messaging_ASCIIIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#define LHR_Protocol_AbsoluteLinearActuatorAxis
#define LHR_Protocol_CumulativeLinearActuatorAxis
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using Messager = LiquidHandlingRobotics::Messaging::ASCIIMessager;
using Core = LiquidHandlingRobotics::Protocol::Core<Messager>;
using Board = LiquidHandlingRobotics::Protocol::Board<Messager>;
using AbsoluteLinearActuatorAxis = LiquidHandlingRobotics::Protocol::LinearActuatorAxis<
  LinearPositionControl::Control::AbsoluteLinearActuator,
  Messager
>;
using CumulativeLinearActuatorAxis = LiquidHandlingRobotics::Protocol::LinearActuatorAxis<
  LinearPositionControl::Control::CumulativeLinearActuator,
  Messager
>;

// Shared Components
LinearPositionControl::Components::Motors motors;
Messager messager;

// Protocol
Core core(messager);
Board board(messager);
AbsoluteLinearActuatorAxis pipettorAxis(messager, motors, LHR_kPipettorParams);
AbsoluteLinearActuatorAxis zAxis(messager, motors, LHR_kVerticalPositionerParams);
CumulativeLinearActuatorAxis yAxis(messager, motors, LHR_kYPositionerParams);
LinearPositionControl::Control::SmoothedCumulativePositionCalibrator yAxisCalibrator(
  yAxis.actuator, yAxis.smoother, LHR_kYPositionerCalibrationParams
);

void updateCommon() {
  messager.update();
  core.update();
  board.update();
  pipettorAxis.update();
  zAxis.update();
}

void connectAxes() {
  pipettorAxis.onConnect();
  // Make the z-axis move up so the syringe doesn't hit anything during y-axis initialization
  zAxis.startDirectMotorDutyControl(255);
  while (!zAxis.state.at(AbsoluteLinearActuatorAxis::State::stallTimeoutStopped)) updateCommon();
  zAxis.startDirectMotorDutyControl(0);
  zAxis.onConnect();

  // Calibrate the y-axis
  while (!yAxisCalibrator.calibrated()) {
    updateCommon();
    yAxisCalibrator.update();
  }
  yAxis.onConnect();
}

void setup() {
  core.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  board.setup();
  pipettorAxis.setup();
  zAxis.setup();
  yAxis.setup();
  yAxisCalibrator.setup();

  messager.establishConnection();
  core.onConnect();
  board.onConnect();
  connectAxes();
}

void loop() {
  updateCommon();
  yAxis.update();
}

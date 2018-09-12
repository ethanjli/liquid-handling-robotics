#ifndef Modules_h
#define Modules_h

// Ensure that we have a messaging system and the core protocol and placeholders
#ifdef LHR_Messaging_FirmataIO
  #undef LHR_Messaging_ASCIIIO
#else
  #define LHR_Messaging_ASCIIIO
#endif
#define LHR_Protocol_Core
#define LHR_Protocol_Placeholder
#include "LiquidHandlingRobotics.h"

// Define default parameter values for each actuator axis.
// Note: we use macros instead of const structs because the const structs use a
// significant amount of SRAM despite only being used for initializing some
// parameters with "nice" values.
#define LHR_kPipettorParams\
  /* actuatorChannelPrefix */ 'p',\
  /* motorPort, potentiometerPin */ M1, A0,\
  /* minPosition, maxPosition */ 35, 1005,\
  /* minDuty, maxDuty */ -255, 255,\
  /* pidKp, pidKd, pidKi, pidSampleTime */ 32.5, 0.4, 0, 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -150, 150,\
  /* swapSensorDirection, swapMotorPolarity */ true, true,\
  /* convergenceTimeout, stallTimeout, timerTimeout */ 150, 150, 2000,\
  /* smootherSnapMultiplier, smootherMax */ 0.01, 1023,\
  /* smootherEnableSleep, smootherActivityThreshold */ true, 4.0
#define LHR_kVerticalPositionerParams\
  /* actuatorChannelPrefix */ 'z',\
  /* motorPort, potentiometerPin */ M2, A1,\
  /* minPosition, maxPosition */ 20, 970,\
  /* minDuty, maxDuty */ -120, 200,\
  /* pidKp, pidKd, pidKi, pidSampleTime */ 10, 0.08, 0, 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -50, 110,\
  /* swapSensorDirectionswapMotorPolarity */ false, false,\
  /* convergenceTimeout, stallTimeout, timerTimeout */ 150, 150, 2000,\
  /* smootherSnapMultiplier, smootherMax */ 0.01, 1023,\
  /* smootherEnableSleep, smootherActivityThreshold */ true, 4.0
#define LHR_kYPositionerParams\
  /* actuatorChannelPrefix */ 'y',\
  /* motorPort, angleSensorId */ M3, 0,\
  /* minPosition, maxPosition */ 0, 720,\
  /* minDuty, maxDuty */ -120, 120,\
  /* pidKp, pidKd, pidKi, pidSampleTime */ 45, 1.25, 0, 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -110, 110,\
  /* swapSensorDirection, swapMotorPolarity */ false, true,\
  /* convergenceTimeout, stallTimeout, timerTimeout */ 150, 150, 5000,\
  /* smootherSnapMultiplier, smootherMax */ 0.01, 800,\
  /* smootherEnableSleep, smootherActivityThreshold */ true, 2.0
#define LHR_kYPositionerCalibrationParams\
  /* calibrationSpeed */ 120

// Define convenience macros for instantiating, setting up, connecting, and updating messaging system

#ifndef DISABLE_LOGGING
#pragma message("INFO: Serial logging enabled.")
  #include <ArduinoLog.h>
  #define LHR_setupLogging(logLevel, logTarget)\
    Log.begin(logLevel, logTarget);
#else
#pragma message("INFO: Serial logging disabled.")
  #define LHR_setupLogging(logLevel, logTarget)
#endif

#ifdef LHR_Messager
  #if defined(LHR_Messaging_FirmataIO) && !defined(LHR_Messaging_ASCIIIO)
#pragma message("INFO: Messaging system can be instantiated with LHR_instantiateMessaging(transport, messager).")
#pragma message("INFO: Messaging system can be set up with LHR_setupMessaging(transport, messager, core).")
#pragma message("INFO: Messaging system can be connected with LHR_connectMessaging(messager).")
#pragma message("INFO: Messaging system can be updated with LHR_updateMessaging(transport, messager).")
    #define LHR_instantiateMessaging(transport, messager)\
      LiquidHandlingRobotics::Transport transport;\
      LiquidHandlingRobotics::Messager messager(transport);\
      LHR_makeFirmataTransportResetCallback(transport);
    #define LHR_setupMessaging(transport, messager, core)\
      core.setup();\
      transport.setup();\
      LHR_attachFirmataTransportResetCallback(transport);\
      messager.setup();
    #define LHR_connectMessaging(transport, messager)\
      messager.establishConnection();
    #define LHR_updateMessaging(transport, messager)\
      transport.update();\
      messager.update();
  #elif defined(LHR_Messaging_ASCIIIO) && !defined(LHR_Messaging_FirmataIO)
#pragma message("INFO: Messaging system can be instantiated with LHR_instantiateMessaging(transport, messager).")
#pragma message("INFO: Messaging system can be set up with LHR_setupMessaging(transport, messager, core).")
#pragma message("INFO: Messaging system can be connected with LHR_connectMessaging(messager).")
#pragma message("INFO: Messaging system can be updated with LHR_updateMessaging(transport, messager).")
    #define LHR_instantiateMessaging(transport, messager)\
      LiquidHandlingRobotics::Messager messager;
    #define LHR_setupMessaging(transport, messager, core)\
      core.setup();\
      messager.setup();\
      LHR_setupLogging(LOG_LEVEL_VERBOSE, &Serial);
    #define LHR_connectMessaging(transport, messager)\
      messager.establishConnection();
    #define LHR_updateMessaging(transport, messager)\
      messager.update();
  #else
#pragma message("WARNING: LiquidHandlingRobotics::Transport must be instantiated manually.")
#pragma message("WARNING: LiquidHandlingRobotics::Messager must be instantiated manually.")
  #endif
#endif

// Define convenience macros for instantiating, setting up, connecting, and updating basic protocol subset

#pragma message("INFO: Basic protocol functionality can be instantiated with LHR_instantiateBasics(core, board).")
#pragma message("INFO: Basic protocol functionality can be set up with LHR_setupBasics(core, board).")
#pragma message("INFO: Basic protocol functionality can be connected with LHR_connectBasics(core, board).")
#pragma message("INFO: Basic protocol functionality can be updated with LHR_updateBasics(core, board).")
#pragma message("INFO: Basic protocol functionality includes the Core protocol subset.")

#if defined(LHR_Board)// && !defined(LHR_Messaging_FirmataIO)
#pragma message("INFO: Basic protocol functionality includes the Board protocol subset.")
  #define LHR_instantiateBoard(board)\
    LiquidHandlingRobotics::Board board(messager);
#else
#pragma message("INFO: Basic protocol functionality does not include the Board protocol subset.")
  #define LHR_instantiateBoard(board)\
    LiquidHandlingRobotics::Protocol::Placeholder board;
#endif

#define LHR_instantiateBasics(core, board)\
  LiquidHandlingRobotics::Core core(messager);\
  LHR_instantiateBoard(board);
#define LHR_setupBasics(core, board)\
  core.setup();\
  board.setup();
#define LHR_connectBasics(core, board)\
  core.onConnect();\
  board.onConnect();
#define LHR_updateBasics(core, board)\
  core.update();\
  board.update();

// Define convenience macros for instantiating, setting up, connecting, and updating standard axes
//
#if defined(LHR_Standard_pipettorAxis) || defined(LHR_Standard_zAxis) || defined(LHR_Standard_yAxis) || defined(LHR_Standard_xAxis)
#pragma message("INFO: Linear actuator protocol functionality can be instantiated with LHR_instantiateAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator, messager, motors).")
#pragma message("INFO: Linear actuator protocol functionality can be set up with LHR_setupAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator).")
#pragma message("INFO: Linear actuator protocol functionality can be connected with LHR_connectAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator).")
#pragma message("INFO: Linear actuator protocol functionality can be updated with LHR_updateAxes(pipettorAxis, zAxis, yAxis, xAxis).")
  #define LHR_Standard_motors
#endif
#ifdef LHR_Standard_motors
  #define LHR_instantiateMotors(motors);\
    LinearPositionControl::Components::Motors motors;
#endif

#ifdef LHR_Standard_pipettorAxis
#pragma message("INFO: Linear actuator protocol functionality includes the pipettor axis.")
  #define LHR_instantiatePipettorAxis(pipettorAxis, messager, motors);\
    LiquidHandlingRobotics::AbsoluteLinearActuatorAxis pipettorAxis(messager, motors, LHR_kPipettorParams);
#else
#pragma message("INFO: Linear actuator protocol functionality does not include the pipettor axis.")
  #define LHR_instantiatePipettorAxis(pipettorAxis, messager, motors);\
    LiquidHandlingRobotics::Protocol::Placeholder pipettorAxis;
#endif

#ifdef LHR_Standard_zAxis
#pragma message("INFO: Linear actuator protocol functionality includes the z axis.")
  #define LHR_instantiateZAxis(zAxis, messager, motors);\
    LiquidHandlingRobotics::AbsoluteLinearActuatorAxis zAxis(messager, motors, LHR_kVerticalPositionerParams);
#else
#pragma message("INFO: Linear actuator protocol functionality does not include the z axis.")
  #define LHR_instantiateZAxis(zAxis, messager, motors);\
    LiquidHandlingRobotics::Protocol::Placeholder zAxis;
#endif

#ifdef LHR_Standard_yAxis
#pragma message("INFO: Linear actuator protocol functionality includes the y axis.")
  #define LHR_instantiateYAxis(yAxis, yAxisCalibrator, messager, motors);\
    LiquidHandlingRobotics::CumulativeLinearActuatorAxis yAxis(messager, motors, LHR_kYPositionerParams);\
    LinearPositionControl::Control::SmoothedCumulativePositionCalibrator yAxisCalibrator(yAxis.actuator, yAxis.smoother, LHR_kYPositionerCalibrationParams);
#else
#pragma message("INFO: Linear actuator protocol functionality does not include the y axis.")
  #define LHR_instantiateYAxis(yAxis, yAxisCalibrator, messager, motors);\
    LiquidHandlingRobotics::Protocol::Placeholder yAxis;\
    LiquidHandlingRobotics::Protocol::Placeholder yAxisCalibrator;
#endif

#ifdef LHR_Standard_xAxis
#pragma message("INFO: Linear actuator protocol functionality includes the x axis.")
  #define LHR_instantiateXAxis(xAxis, xAxisCalibrator, messager, motors);\
    LiquidHandlingRobotics::CumulativeLinearActuatorAxis xAxis(messager, motors, LHR_kXPositionerParams);\
    LinearPositionControl::Control::SmoothedCumulativePositionCalibrator xAxisCalibrator(xAxis.actuator, xAxis.smoother, LHR_kXPositionerCalibrationParams);
#else
#pragma message("INFO: Linear actuator protocol functionality does not include the x axis.")
  #define LHR_instantiateXAxis(xAxis, xAxisCalibrator, messager, motors);\
    LiquidHandlingRobotics::Protocol::Placeholder xAxis;\
    LiquidHandlingRobotics::Protocol::Placeholder xAxisCalibrator;
#endif

#if defined(LHR_Standard_pipettorAxis) || defined(LHR_Standard_zAxis) || defined(LHR_Standard_yAxis) || defined(LHR_Standard_xAxis)
  #define LHR_instantiateAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator, messager, motors);\
    LHR_instantiateMotors(motors);\
    LHR_instantiatePipettorAxis(pipettorAxis, messager, motors);\
    LHR_instantiateZAxis(zAxis, messager, motors);\
    LHR_instantiateYAxis(yAxis, yAxisCalibrator, messager, motors);\
    LHR_instantiateXAxis(xAxis, xAxisCalibrator, messager, motors);
  #define LHR_setupAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator)\
    pipettorAxis.setup();\
    zAxis.setup();\
    yAxis.setup(); yAxisCalibrator.setup();\
    xAxis.setup(); xAxisCalibrator.setup();
  #define LHR_updateAxes(pipettorAxis, zAxis, yAxis, xAxis)\
    pipettorAxis.update();\
    zAxis.update();\
    yAxis.update();\
    xAxis.update();
  #define LHR_updateAbsoluteAxes(pipettorAxis, zAxis)\
    pipettorAxis.update();\
    zAxis.update();
  #define LHR_calibrateAxis(axis, calibrator, transport, messager, core, board, pipettorAxis, zAxis)\
    while (!axis.calibrated()) {\
      LHR_updateMessaging(transport, messager);\
      LHR_updateBasics(core, board);\
      LHR_updateAbsoluteAxes(pipettorAxis, zAxis);\
      calibrator.update();\
    }\
    axis.onConnect();
#endif

#ifdef LHR_Standard_zAxis
  #define LHR_Standard_connectZAxis(zAxis, initializationSpeed, transport, messager, core, board, pipettorAxis)\
    zAxis.startDirectMotorDutyControl(initializationSpeed);\
    while (!zAxis.state.at(LiquidHandlingRobotics::Protocol::States::LinearActuatorMode::stallTimeoutStopped)) {\
      LHR_updateMessaging(transport, messager);\
      LHR_updateBasics(core, board);\
      LHR_updateAbsoluteAxes(pipettorAxis, zAxis);\
    }\
    zAxis.startDirectMotorDutyControl(0);\
    zAxis.onConnect();
#else
  #define LHR_Standard_connectZAxis(zAxis, initializationSpeed, transport, messager, core, board, pipettorAxis)\
    zAxis.onConnect();
#endif

#ifdef LHR_Standard_yAxis
  #define LHR_Standard_connectYAxis(yAxis, yAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis)\
    while (!yAxisCalibrator.calibrated()) {\
      LHR_updateMessaging(transport, messager);\
      LHR_updateBasics(core, board);\
      LHR_updateAbsoluteAxes(pipettorAxis, zAxis);\
      yAxisCalibrator.update();\
    }\
    yAxis.onConnect();
#else
  #define LHR_Standard_connectYAxis(yAxis, yAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis)
#endif

#ifdef LHR_Standard_xAxis
  #define LHR_Standard_connectXAxis(xAxis, xAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis, yAxis)\
    while (!xAxisCalibrator.calibrated()) {\
      LHR_updateMessaging(transport, messager);\
      LHR_updateBasics(core, board);\
      LHR_updateAbsoluteAxes(pipettorAxis, zAxis);\
      xAxis.update();\
      xAxisCalibrator.update();\
    }\
    xAxis.onConnect();
#else
  #define LHR_Standard_connectXAxis(xAxis, xAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis, yAxis)
#endif

#if defined(LHR_Standard_zAxis) && (defined(LHR_Standard_yAxis) || defined(LHR_Standard_xAxis))
  #define LHR_connectAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator, transport, messager, core, board)\
    pipettorAxis.onConnect();\
    LHR_Standard_connectZAxis(zAxis, 255, transport, messager, core, board, pipettorAxis);\
    LHR_Standard_connectYAxis(yAxis, yAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis);\
    LHR_Standard_connectXAxis(xAxis, xAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis, yAxis);
#elif defined(LHR_Standard_pipettorAxis) || defined(LHR_Standard_zAxis) || defined(LHR_Standard_yAxis) || defined(LHR_Standard_xAxis)
  #define LHR_connectAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator, transport, messager, core, board)\
    pipettorAxis.onConnect();\
    zAxis.onConnect();\
    LHR_Standard_connectYAxis(yAxis, yAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis);\
    LHR_Standard_connectXAxis(xAxis, xAxisCalibrator, transport, messager, core, board, pipettorAxis, zAxis, yAxis);
#endif

#if defined(LHR_Standard_pipettorAxis) || defined(LHR_Standard_zAxis) || defined(LHR_Standard_yAxis) || defined(LHR_Standard_xAxis)
  #define LHR_connect(transport, messager, core, board, pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator)\
    LHR_connectMessaging(transport, messager);\
    LHR_connectBasics(core, board);\
    LHR_connectAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator, transport, messager, core, board);
#endif

#endif


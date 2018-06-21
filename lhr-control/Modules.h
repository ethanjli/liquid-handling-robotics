#ifndef Modules_h
#define Modules_h

// These headers must be manually included!
//#include <AbsoluteLinearPositionControl.h>
//#include <CumulativeLinearPositionControl.h>
#include "LinearActuatorModule.h"

namespace LiquidHandlingRobotics {

#ifdef AbsoluteLinearPositionControl_h
template<class Messager>
using AbsoluteLinearActuator = LinearActuatorModule<
  LinearPositionControl::AbsoluteLinearActuator,
  Messager
>;
#endif

#ifdef CumulativeLinearPositionControl_h
template<class Messager>
using CumulativeLinearActuator = LinearActuatorModule<
  LinearPositionControl::CumulativeLinearActuator,
  Messager
>;
#endif

}

// Note: we use macros instead of const structs because the const structs use a
// significant amount of SRAM despite only being used for initializing some
// parameters with "nice" values.

#define kPipettorParams\
  /* actuatorChannelPrefix */ 'p',\
  /* motorPort, potentiometerPin */ M1, A0,\
  /* minPosition, maxPosition */ 20, 975,\
  /* minDuty, maxDuty */ -255, 255,\
  /* pidKp, pidKd, pidKi, pidSampleTime */ 30, 1, 0.1, 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -180, 180,\
  /* swapMotorPolarity */ false,\
  /* convergenceTimeout, stallTimeout, timerTimeout */ 100, 200, 10000,\
  /* smootherSnapMultiplier, smootherMax */ 0.01, 1023,\
  /* smootherEnableSleep, smootherActivityThreshold */ true, 4.0

#define kVerticalPositionerParams\
  /* actuatorChannelPrefix */ 'z',\
  /* motorPort, potentiometerPin */ M2, A1,\
  /* minPosition, maxPosition */ 20, 970,\
  /* minDuty, maxDuty */ -255, 255,\
  /* pidKp, pidKd, pidKi, pidSampleTime */ 8, 0.2, 0.2, 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -60, 120,\
  /* swapMotorPolarity */ false,\
  /* convergenceTimeout, stallTimeout, timerTimeout */ 100, 200, 10000,\
  /* smootherSnapMultiplier, smootherMax */ 0.01, 1023,\
  /* smootherEnableSleep, smootherActivityThreshold */ true, 4.0

#define kYPositionerParams\
  /* actuatorChannelPrefix */ 'y',\
  /* motorPort, angleSensorId */ M3, 0,\
  /* minPosition, maxPosition */ 0, 700,\
  /* minDuty, maxDuty */ -200, 200,\
  /* pidKp, pidKd, pidKi, pidSampleTime */ 10, 0, 0, 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -70, 70,\
  /* swapMotorPolarity */ false,\
  /* convergenceTimeout, stallTimeout, timerTimeout */ 150, 200, 20000,\
  /* smootherSnapMultiplier, smootherMax */ 0.01, 800,\
  /* smootherEnableSleep, smootherActivityThreshold */ true, 2.0

#define kYPositionerCalibrationParams\
  /* calibrationSpeed */ 200

#endif


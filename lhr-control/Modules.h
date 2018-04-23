#ifndef Modules_h
#define Modules_h

#include <AbsoluteLinearPositionControl.h>
#include <CumulativeLinearPositionControl.h>
#include "LinearActuatorModule.h"

namespace LiquidHandlingRobotics {

using AbsoluteLinearActuator = LinearActuatorModule<LinearPositionControl::AbsoluteLinearActuator>;
using CumulativeLinearActuator = LinearActuatorModule<LinearPositionControl::CumulativeLinearActuator>;

}

// Note: we use macros instead of const structs because the const structs use a
// significant amount of SRAM despite only being used for initializing some
// parameters with "nice" values.

#define kPipettorParams\
  /* actuatorChannelPrefix */ 'p',\
  /* motorPort, potentiometerPin */ M1, A0,\
  /* minPosition, maxPosition */ 100, 975,\
  /* minDuty, maxDuty */ -255, 255,\
  /* pidKp, pidKd, pidKi */ 20, 0.1, 0.1,\
  /* pidSampleTime */ 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -180, 180,\
  /* swapMotorPolarity */ false,\
  /* convergenceDelay */ 100,\
  /* stallTimeout, stallSmootherSnapMultiplier, stallSmootherMax */ 200, 0.01, 1023,\
  /* stallSmootherEnableSleep, stallSmootherActivityThreshold */ true, 4.0

#define kVerticalPositionerParams\
  /* actuatorChannelPrefix */ 'z',\
  /* motorPort, potentiometerPin */ M2, A1,\
  /* minPosition, maxPosition */ 20, 970,\
  /* minDuty, maxDuty */ -255, 255,\
  /* pidKp, pidKd, pidKi */ 8, 0.2, 0.1,\
  /* pidSampleTime */ 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -60, 120,\
  /* swapMotorPolarity */ false,\
  /* convergenceDelay */ 100,\
  /* stallTimeout, stallSmootherSnapMultiplier, stallSmootherMax */ 200, 0.01, 1023,\
  /* stallSmootherEnableSleep, stallSmootherActivityThreshold */ true, 4.0

#define kYPositionerParams\
  /* actuatorChannelPrefix */ 'y',\
  /* motorPort, angleSensorId */ M3, 0,\
  /* minPosition, maxPosition */ 0, 700,\
  /* minDuty, maxDuty */ -200, 200,\
  /* pidKp, pidKd, pidKi */ 10, 0.1, 0.1,\
  /* pidSampleTime */ 10,\
  /* feedforward */ 0,\
  /* brakeLowerThreshold, brakeUpperThreshold */ -80, 80,\
  /* swapMotorPolarity */ false,\
  /* convergenceDelay */ 100,\
  /* stallTimeout, stallSmootherSnapMultiplier, stallSmootherMax */ 200, 0.01, 800,\
  /* stallSmootherEnableSleep, stallSmootherActivityThreshold */ true, 2.0

#define kYPositionerCalibrationParams\
  /* calibrationSpeed */ 200

#endif


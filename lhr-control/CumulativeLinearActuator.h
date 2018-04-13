#ifndef CumulativeLinearActuator_h
#define CumulativeLinearActuator_h

#include <CumulativeLinearPositionControl.h>
#include <ASCIISerialIO.h>

#include "LinearActuatorModule.h"

namespace LiquidHandlingRobotics {

struct CumulativeLinearActuatorParams {
  using LinearActuator = LinearPositionControl::CumulativeLinearActuator;

  char actuatorChannelPrefix;

  MotorPort motorPort;

  int minPosition;
  int maxPosition;

  int minDuty;
  int maxDuty;

  double pidKp;
  double pidKd;
  double pidKi;

  int pidSampleTime;

  int feedforward;

  int brakeLowerThreshold;
  int brakeUpperThreshold;

  bool swapMotorPolarity;

  int convergenceDelay;

  int stallTimeout;
  float stallSmootherSnapMultiplier;
  int stallSmootherMax;
  bool stallSmootherEnableSleep;
  float stallSmootherActivityThreshold;
};

using CumulativeLinearActuator = LinearActuatorModule<CumulativeLinearActuatorParams>;

}

#endif


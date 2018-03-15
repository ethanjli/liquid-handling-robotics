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

  double pidKp;
  double pidKd;
  double pidKi;
  int pidSampleTime;

  int feedforward;
  int brakeLowerThreshold;
  int brakeUpperThreshold;

  bool swapMotorPolarity;
  int convergenceDelay;

  int minDuty;
  int maxDuty;
};

using CumulativeLinearActuator = LinearActuatorModule<CumulativeLinearActuatorParams>;

}

#endif


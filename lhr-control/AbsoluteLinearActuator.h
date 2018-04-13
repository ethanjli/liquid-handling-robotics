#ifndef AbsoluteLinearActuator_h
#define AbsoluteLinearActuator_h

#include <AbsoluteLinearPositionControl.h>
#include <ASCIISerialIO.h>

#include "LinearActuatorModule.h"

namespace LiquidHandlingRobotics {

struct AbsoluteLinearActuatorParams {
  using LinearActuator = LinearPositionControl::AbsoluteLinearActuator;

  char actuatorChannelPrefix;

  MotorPort motorPort;
  uint8_t potentiometerPin;

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

using AbsoluteLinearActuator = LinearActuatorModule<AbsoluteLinearActuatorParams>;

}

#endif


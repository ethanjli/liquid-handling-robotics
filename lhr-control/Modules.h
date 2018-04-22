#ifndef Modules_h
#define Modules_h

#include <AbsoluteLinearActuator.h>
#include <CumulativeLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams kPipettorParams = {
  // actuatorChannelPrefix
  'p',
  // motorPort, potentiometerPin
  M1, A0,
  // minPosition, maxPosition
  100, 975,
  // minDuty, maxDuty
  -255, 255,
  // pidKp, pidKd, pidKi
  20, 0.1, 0.1,
  // pidSampleTime
  10,
  // feedforward
  0,
  // brakeLowerThreshold, brakeUpperThreshold
  -160, 160,
  // swapMotorPolarity
  false,
  // convergenceDelay
  100,
  // stallTimeout, stallSmootherSnapMultiplier, stallSmootherMax,
  200, 0.01, 1023,
  // stallSmootherEnableSleep, stallSmootherActivityThreshold
  true, 4.0
};

const AbsoluteLinearActuatorParams kVerticalPositionerParams = {
  // actuatorChannelPrefix
  'z',
  // motorPort, potentiometerPin
  M2, A1,
  // minPosition, maxPosition
  20, 970,
  // minDuty, maxDuty
  -255, 255,
  // pidKp, pidKd, pidKi
  8, 0.2, 0.1,
  // pidSampleTime
  10,
  // feedforward
  0,
  // brakeLowerThreshold, brakeUpperThreshold
  -100, 100,
  // swapMotorPolarity
  false,
  // convergenceDelay
  100,
  // stallTimeout, stallSmootherSnapMultiplier, stallSmootherMax,
  200, 0.01, 1023,
  // stallSmootherEnableSleep, stallSmootherActivityThreshold
  true, 4.0
};

const CumulativeLinearActuatorParams kYPositionerParams = {
  // actuatorChannelPrefix
  'y',
  // motorPort
  M3,
  // minPosition, maxPosition
  0, 700,
  // minDuty, maxDuty
  -200, 200,
  // pidKp, pidKd, pidKi
  10, 0.1, 0.1,
  // pidSampleTime
  10,
  // feedforward
  0,
  // brakeLowerThreshold, brakeUpperThreshold
  -60, 60,
  // swapMotorPolarity
  false,
  // convergenceDelay
  100,
  // stallTimeout, stallSmootherSnapMultiplier, stallSmootherMax,
  200, 0.01, 800,
  // stallSmootherEnableSleep, stallSmootherActivityThreshold
  true, 2.0
};

}

#endif


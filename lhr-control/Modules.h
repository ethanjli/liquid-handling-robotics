#ifndef Modules_h
#define Modules_h

#include <AbsoluteLinearActuator.h>
#include <CumulativeLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams pipettorParams = {
  // actuatorChannelPrefix
  'p',
  // motorPort, potentiometerPin
  M1, A0,
  // minPosition, maxPosition
  100, 975,
  // pidKp, pidKd, pidKi
  20, 0.1, 0.1,
  // pidSampleTime
  10,
  // feedforward
  0,
  // brakeLowerThreshold, brakeUpperThreshold
  -140, 140,
  // swapMotorPolarity
  false,
  // convergenceDelay
  100,
  // minDuty, maxDuty
  -255, 255
};

const AbsoluteLinearActuatorParams verticalPositionerParams = {
  // actuatorChannelPrefix
  'z',
  // motorPort, potentiometerPin
  M2, A1,
  // minPosition, maxPosition
  20, 970,
  // pidKp, pidKd, pidKi
  8, 0.1, 0.2,
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
  // minDuty, maxDuty
  -255, 255
};

const CumulativeLinearActuatorParams yPositionerParams = {
  // actuatorChannelPrefix
  'y',
  // motorPort
  M3,
  // minPosition, maxPosition
  0, 700,
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
  // minDuty, maxDuty
  -200, 200
};

}

#endif


#ifndef Modules_h
#define Modules_h

#include <AbsoluteLinearActuator.h>
#include <CumulativeLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams pipettorParams = {
  'p',
  M1, A0, 100, 975,
  20, 0.1, 0.1, 10,
  0, -100, 100,
  false, 100,
  -255, 255
};

const AbsoluteLinearActuatorParams verticalPositionerParams = {
  'z',
  M2, A1, 20, 970,
  8, 0.1, 0.2, 10,
  0, -100, 100,
  false, 100,
  -255, 255
};

const CumulativeLinearActuatorParams yPositionerParams = {
  'y',
  M3, 0, 700,
  10, 0.1, 0.1, 10,
  0, -60, 60,
  false, 100,
  -200, 200
};

}

#endif


#ifndef Pipettor_h
#define Pipettor_h

#include <AbsoluteLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams pipettorParams = {
  'p',
  M1, A0, 400, 983,
  20, 0.1, 0.1, 10,
  0, -80, 80,
  false, 100,
  -255, 255
};

}

#endif


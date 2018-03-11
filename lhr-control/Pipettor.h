#ifndef Pipettor_h
#define Pipettor_h

#include <AbsoluteLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams pipettorParams = {
  'p',
  M1, A0, 100, 980,
  20, 0.1, 0.1, 10,
  0, -100, 100,
  false, 100,
  -255, 255
};

}

#endif


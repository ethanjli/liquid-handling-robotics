#ifndef Pipettor_h
#define Pipettor_h

#include <AbsoluteLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams pipettorParams = {
  'p',
  M1, A0, 11, 999,
  8, 0.1, 0.1, 20,
  7, 80,
  false, 100
};

}

#endif


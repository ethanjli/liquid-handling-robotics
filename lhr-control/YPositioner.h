#ifndef YPositioner_h
#define YPositioner_h

#include <CumulativeLinearActuator.h>

namespace LiquidHandlingRobotics {

const CumulativeLinearActuatorParams yPositionerParams = {
  'y',
  M3, 155, 720 + 155,
  10, 0.1, 0.1, 10,
  0, -60, 60,
  false, 100,
  -200, 200
};

}

#endif


#ifndef VerticalPositioner_h
#define VerticalPositioner_h

#include <AbsoluteLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams verticalPositionerParams = {
  'z',
  M2, A1, 20, 970,
  8, 0.1, 0.2, 10,
  0, -100, 100,
  false, 100,
  -255, 255
};

}

#endif


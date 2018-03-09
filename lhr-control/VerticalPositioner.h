#ifndef VerticalPositioner_h
#define VerticalPositioner_h

#include <AbsoluteLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams verticalPositionerParams = {
  'z',
  M2, A1, 11, 999,
  6, 0.1, 0.1, 10,
  0, -60, 100,
  false, 100,
  -60, 255
};

}

#endif


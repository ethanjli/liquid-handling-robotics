#ifndef VerticalPositioner_h
#define VerticalPositioner_h

#include <AbsoluteLinearActuator.h>

namespace LiquidHandlingRobotics {

const AbsoluteLinearActuatorParams verticalPositionerParams = {
  'z',
  M2, A1, 11, 999,
  8, 0.1, 0.2, 10,
  8, 80,
  false, 100
};

}

#endif


#include "CumulativeLinearActuator.h"

namespace LiquidHandlingRobotics {

// CumulativeLinearActuator

template<>
LinearActuatorModule<CumulativeLinearActuatorParams>::LinearActuatorModule(
    MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
    const CumulativeLinearActuatorParams &params
) :
  messageParser(messageParser),
  actuator(
    motors, params.motorPort,
    params.minPosition, params.maxPosition,
    params.pidKp, params.pidKd, params.pidKi, params.pidSampleTime,
    params.swapMotorPolarity, params.feedforward,
    params.brakeLowerThreshold, params.brakeUpperThreshold,
    params.minDuty, params.maxDuty
  ),
  convergenceDelay(params.convergenceDelay), moduleChannel(params.actuatorChannelPrefix)
{}

}


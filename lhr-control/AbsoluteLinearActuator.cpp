#include "AbsoluteLinearActuator.h"

namespace LiquidHandlingRobotics {

// AbsoluteLinearActuator

template<>
LinearActuatorModule<AbsoluteLinearActuatorParams>::LinearActuatorModule(
    MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
    const AbsoluteLinearActuatorParams &params
) :
  messageParser(messageParser),
  actuator(
    motors, params.motorPort,
    params.potentiometerPin, params.minPosition, params.maxPosition,
    params.pidKp, params.pidKd, params.pidKi, params.pidSampleTime,
    params.swapMotorPolarity, params.feedforward,
    params.brakeLowerThreshold, params.brakeUpperThreshold,
    params.minDuty, params.maxDuty
  ),
  convergenceDelay(params.convergenceDelay)
{
  targetingChannel[0] = params.actuatorChannelPrefix;
  reportingConvergenceChannel[0] = params.actuatorChannelPrefix;
  reportingStreamingChannel[0] = params.actuatorChannelPrefix;
}

}


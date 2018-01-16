#define LIBCALL_ENABLEINTERRUPT
#include "AbsoluteLinearActuator.h"

namespace LiquidHandlingRobotics {

// AbsoluteLinearActuator

AbsoluteLinearActuator::AbsoluteLinearActuator(
    MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
    const AbsoluteLinearActuatorParams &params
) :
  messageParser(messageParser),
  actuator(
    motors, params.motorPort,
    params.potentiometerPin, params.minPosition, params.maxPosition,
    params.pidKp, params.pidKd, params.pidKi, params.pidSampleTime,
    params.swapMotorPolarity, params.feedforward, params.brakeThreshold
  ),
  convergenceDelay(params.convergenceDelay)
{
  thresholdChannel[0] = params.actuatorChannelPrefix;
  convergenceChannel[0] = params.actuatorChannelPrefix;
  streamingChannel[0] = params.actuatorChannelPrefix;
}

void AbsoluteLinearActuator::setup() {
  actuator.setup();
}

void AbsoluteLinearActuator::update() {
  actuator.update();

  if (messageParser.justReceived(thresholdChannel)) {
    actuator.pid.setSetpoint(messageParser.payload);
    reportedConvergence = false;
  }

  if (converged(convergenceDelay) && !reportedConvergence) reportConvergencePosition();
  if (streamingPosition) reportStreamingPosition();
}

bool AbsoluteLinearActuator::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

void AbsoluteLinearActuator::reportConvergencePosition() {
  sendMessage(convergenceChannel, actuator.pid.getInput());
  reportedConvergence = true;
}

void AbsoluteLinearActuator::reportStreamingPosition() {
  sendMessage(streamingChannel, actuator.pid.getInput());
}

}


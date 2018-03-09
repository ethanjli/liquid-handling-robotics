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

void AbsoluteLinearActuator::setup() {
  actuator.setup();
}

void AbsoluteLinearActuator::update() {
  actuator.update();

  if (messageParser.justReceived(targetingChannel)) {
    actuator.pid.setSetpoint(messageParser.payload);
    reportedConvergence = false;
  }
  if (messageParser.justReceived(reportingStreamingChannel)) {
    streamingPosition = (messageParser.payload > 0);
  }

  if (converged(convergenceDelay) && !reportedConvergence) reportConvergencePosition();
  if (streamingPosition) reportStreamingPosition();
}

bool AbsoluteLinearActuator::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

void AbsoluteLinearActuator::reportConvergencePosition() {
  sendMessage(reportingConvergenceChannel, actuator.pid.getInput());
  reportedConvergence = true;
}

void AbsoluteLinearActuator::reportStreamingPosition() {
  sendMessage(reportingStreamingChannel, actuator.pid.getInput());
}

}


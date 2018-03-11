#include "CumulativeLinearActuator.h"

namespace LiquidHandlingRobotics {

// CumulativeLinearActuator

CumulativeLinearActuator::CumulativeLinearActuator(
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
  convergenceDelay(params.convergenceDelay)
{
  targetingChannel[0] = params.actuatorChannelPrefix;
  reportingConvergenceChannel[0] = params.actuatorChannelPrefix;
  reportingStreamingChannel[0] = params.actuatorChannelPrefix;
}

void CumulativeLinearActuator::setup() {
  actuator.setup();
}

void CumulativeLinearActuator::update() {
  actuator.update();

  if (messageParser.justReceived(targetingChannel)) {
    actuator.pid.setSetpoint(messageParser.payload);
    reportedConvergence = false;
    actuator.unfreeze();
  }
  if (messageParser.justReceived(reportingStreamingChannel)) {
    streamingPosition = (messageParser.payload > 0);
  }

  if (converged(convergenceDelay) && !reportedConvergence) {
    actuator.freeze();
    reportConvergencePosition();
  }
  if (streamingPosition) reportStreamingPosition();
}

bool CumulativeLinearActuator::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

void CumulativeLinearActuator::reportConvergencePosition() {
  sendMessage(reportingConvergenceChannel, actuator.pid.getInput());
  reportedConvergence = true;
}

void CumulativeLinearActuator::reportStreamingPosition() {
  sendMessage(reportingStreamingChannel, actuator.pid.getInput());
}

}


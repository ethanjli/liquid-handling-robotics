#define LIBCALL_ENABLEINTERRUPT
#include "Pipettor.h"

namespace LiquidHandlingRobotics {

// Pipettor

Pipettor::Pipettor(
    ChannelParser &channelParser, IntParser &intParser,
    LinearPositionControl::Components::Motors &motors, MotorPort motorPort,
    uint8_t potentiometerPin, int minPosition, int maxPosition,
    double pidKp, double pidKd, double pidKi, int pidSampleTime,
    bool swapMotorPolarity, int feedforward, int brakeThreshold,
    unsigned int convergenceDelay
) :
  channelParser(channelParser), intParser(intParser),
  actuator(
    motors, motorPort,
    potentiometerPin, minPosition, maxPosition,
    pidKp, pidKd, pidKi, pidSampleTime,
    swapMotorPolarity, feedforward, brakeThreshold
  ),
  convergenceDelay(convergenceDelay)
{
}

void Pipettor::setup() {
  actuator.setup();
}

void Pipettor::update() {
  actuator.update();

  if (channelParser.justUpdated && strcmp(channelParser.channel, "pt") == 0) {
    Serial.println("Need to update setpoint!");
  }

  //actuator.pid.setSetpoint(setpointParser.result.current());

  //if (setpointParser.justUpdated) {
  //  reportedConvergence = false;
  //}

  if (converged(convergenceDelay) && !reportedConvergence) reportConvergencePosition();
  if (streamingPosition) reportStreamingPosition();
}

bool Pipettor::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

void Pipettor::reportConvergencePosition() {
  sendMessage("pc", actuator.pid.getInput());
  reportedConvergence = true;
}

void Pipettor::reportStreamingPosition() {
  sendMessage("ps", actuator.pid.getInput());
}

}


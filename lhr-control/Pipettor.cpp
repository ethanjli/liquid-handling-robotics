#define LIBCALL_ENABLEINTERRUPT
#include "Pipettor.h"

namespace LiquidHandlingRobotics {

// Pipettor

Pipettor::Pipettor(
    MessageParser &messageParser,
    LinearPositionControl::Components::Motors &motors, MotorPort motorPort,
    uint8_t potentiometerPin, int minPosition, int maxPosition,
    double pidKp, double pidKd, double pidKi, int pidSampleTime,
    bool swapMotorPolarity, int feedforward, int brakeThreshold,
    unsigned int convergenceDelay
) :
  messageParser(messageParser),
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

  if (messageParser.justReceived("pt")) {
    actuator.pid.setSetpoint(messageParser.payload);
    reportedConvergence = false;
  }

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


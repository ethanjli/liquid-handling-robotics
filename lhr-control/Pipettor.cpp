#define LIBCALL_ENABLEINTERRUPT
#include "Pipettor.h"

namespace LiquidHandlingRobotics {

// Pipettor

Pipettor::Pipettor(
    LinearPositionControl::Components::Motors &motors, MotorPort motorPort,
    uint8_t potentiometerPin, int minPosition, int maxPosition,
    double pidKp, double pidKd, double pidKi, int pidSampleTime,
    bool swapMotorPolarity, int feedforward, int brakeThreshold,
    unsigned int convergenceDelay
) :
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
  setpointParser.setup();
}

void Pipettor::update() {
  actuator.update();

  setpointParser.update();
  actuator.pid.setSetpoint(setpointParser.result.current());

  if (setpointParser.justUpdated) {
    reportedConvergence = false;
    setpointParser.justUpdated = false;
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


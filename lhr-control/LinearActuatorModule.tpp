#ifndef LinearActuatorModule_tpp
#define LinearActuatorModule_tpp

namespace LiquidHandlingRobotics {

// LinearActuatorModule

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::setup() {
  actuator.setup();
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::update() {
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

template <class LinearActuatorParams>
bool LinearActuatorModule<LinearActuatorParams>::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::reportConvergencePosition() {
  sendMessage(reportingConvergenceChannel, actuator.pid.getInput());
  reportedConvergence = true;
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::reportStreamingPosition() {
  sendMessage(reportingStreamingChannel, actuator.pid.getInput());
}

}

#endif


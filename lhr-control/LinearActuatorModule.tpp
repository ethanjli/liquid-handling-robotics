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

  if (messageParser.justReceived() && messageParser.channel[0] == moduleChannel) {
    onReceivedMessage();
  }

  if (converged(convergenceDelay) && !reportedConvergence) {
    actuator.freeze();
    if (reportingConvergencePosition) reportConvergencePosition();
  }
  if (reportingStreamingPosition) reportStreamingPosition();
}

template <class LinearActuatorParams>
bool LinearActuatorModule<LinearActuatorParams>::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::reportConvergencePosition() {
  sendChannelStart();
  sendChannelChar(moduleChannel);
  sendChannelChar(kReportingChannel);
  sendChannelChar(kReportingConvergenceChannel);
  sendChannelEnd();
  sendPayload(actuator.pid.getInput());
  reportedConvergence = true;
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::reportStreamingPosition() {
  sendChannelStart();
  sendChannelChar(moduleChannel);
  sendChannelChar(kReportingChannel);
  sendChannelChar(kReportingStreamingChannel);
  sendChannelEnd();
  sendPayload(actuator.pid.getInput());
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onReceivedMessage() {
  switch (messageParser.channel[1]) {
    case kConstantsChannel:
      onConstantsMessage();
      break;
    case kLimitsChannel:
      onLimitsMessage();
      break;
    case kReportingChannel:
      onReportingMessage();
      break;
    case kTargetingChannel:
      onTargetingMessage();
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onConstantsMessage() {
  switch (messageParser.channel[2]) {
    case kConstantsProportionalChannel:
      actuator.pid.setKp((float) messageParser.payload / 100.0);
      break;
    case kConstantsDerivativeChannel:
      actuator.pid.setKd((float) messageParser.payload / 100.0);
      break;
    case kConstantsIntegralChannel:
      actuator.pid.setKi((float) messageParser.payload / 100.0);
      break;
    case kConstantsFeedforwardChannel:
      actuator.speedAdjuster.speedBias = messageParser.payload;
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onLimitsMessage() {
  switch (messageParser.channel[2]) {
    case kLimitsPositionChannel:
      switch (messageParser.channel[3]) {
        case kLimitsLowerSubchannel:
          actuator.pid.setMinInput(messageParser.payload);
          break;
        case kLimitsUpperSubchannel:
          actuator.pid.setMaxInput(messageParser.payload);
          break;
      }
      break;
    case kLimitsDutyChannel:
      switch (messageParser.channel[3]) {
        case kLimitsLowerSubchannel:
          actuator.pid.setMinOutput(messageParser.payload);
          break;
        case kLimitsUpperSubchannel:
          actuator.pid.setMaxOutput(messageParser.payload);
          break;
      }
      break;
    case kLimitsBrakeChannel:
      switch (messageParser.channel[3]) {
        case kLimitsLowerSubchannel:
          actuator.speedAdjuster.brakeLowerThreshold = messageParser.payload;
          break;
        case kLimitsUpperSubchannel:
          actuator.speedAdjuster.brakeUpperThreshold = messageParser.payload;
          break;
      }
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onReportingMessage() {
  switch (messageParser.channel[2]) {
    case kReportingConvergenceChannel:
      reportingConvergencePosition = (messageParser.payload > 0);
      break;
    case kReportingStreamingChannel:
      reportingStreamingPosition = (messageParser.payload > 0);
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onTargetingMessage() {
  actuator.pid.setSetpoint(messageParser.payload);
  reportedConvergence = false;
  actuator.unfreeze();
}

}

#endif


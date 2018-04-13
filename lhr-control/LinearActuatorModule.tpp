#ifndef LinearActuatorModule_tpp
#define LinearActuatorModule_tpp

namespace LiquidHandlingRobotics {

// LinearActuatorModule

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::setup() {
  actuator.setup();
  smoother.setup();
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::update() {
  actuator.update();
  smoother.update();

  if (messageParser.justReceived() && messageParser.channel[0] == moduleChannel) {
    onReceivedMessage();
  }

  if (!reportedConvergence && !reportedStallTimeout) {
    if (converged(convergenceDelay)) {
      actuator.freeze(true);
      if (reportingConvergencePosition) reportPosition(kReportingConvergenceChannel);
    } else if (stalled(stallTimeout)) {
      actuator.freeze(true);
      if (reportingStallTimeoutPosition) reportPosition(kReportingStallTimeoutChannel);
    }
  }
  if (streamingPositionReportInterval > 0) {
    if (streamingPositionClock == 0) reportPosition(kReportingStreamingChannel);
    streamingPositionClock = (streamingPositionClock + 1) % streamingPositionReportInterval;
  }
  if (queryPositionCountdown > 0) {
    reportPosition(kReportingQueryChannel);
    --queryPositionCountdown;
  }
}

template <class LinearActuatorParams>
bool LinearActuatorModule<LinearActuatorParams>::converged(unsigned int convergenceTime) {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

template <class LinearActuatorParams>
bool LinearActuatorModule<LinearActuatorParams>::stalled(unsigned int stallTime) {
  return actuator.speedAdjuster.output.current() != 0 &&
    actuator.pid.setpoint.settled(stallTime) &&
    smoother.output.settled(stallTime);
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::reportPosition(char reportingChannel) {
  sendChannelStart();
  sendChannelChar(moduleChannel);
  sendChannelChar(kReportingChannel);
  sendChannelChar(reportingChannel);
  sendChannelEnd();
  sendPayload(actuator.position.current());
  switch (reportingChannel) {
    case kReportingConvergenceChannel:
      reportedConvergence = true;
      break;
    case kReportingStallTimeoutChannel:
      reportedStallTimeout = true;
      break;
  }
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
      reportPosition(kReportingStreamingChannel);
      streamingPositionReportInterval = max(messageParser.payload, 0);
      streamingPositionClock = 0;
      break;
    case kReportingQueryChannel:
      reportPosition(kReportingQueryChannel);
      queryPositionCountdown = max(messageParser.payload, 0);
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onTargetingMessage() {
  actuator.pid.setSetpoint(messageParser.payload);
  reportedConvergence = false;
  reportedStallTimeout = false;
  actuator.unfreeze();
}

}

#endif


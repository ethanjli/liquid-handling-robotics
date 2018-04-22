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
    onReceivedMessage(1);
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
bool LinearActuatorModule<LinearActuatorParams>::converged(unsigned int convergenceTime) const {
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime);
}

template <class LinearActuatorParams>
bool LinearActuatorModule<LinearActuatorParams>::stalled(unsigned int stallTime) const {
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
void LinearActuatorModule<LinearActuatorParams>::onReceivedMessage(unsigned int channelParsedLength) {
  switch (messageParser.channel[channelParsedLength]) {
    case kConstantsChannel:
      onConstantsMessage(channelParsedLength + 1);
      break;
    case kLimitsChannel:
      onLimitsMessage(channelParsedLength + 1);
      break;
    case kReportingChannel:
      onReportingMessage(channelParsedLength + 1);
      break;
    case kTargetingChannel:
      onTargetingMessage(channelParsedLength + 1);
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onConstantsMessage(unsigned int channelParsedLength) {
  switch (messageParser.channel[channelParsedLength]) {
    case kConstantsProportionalChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.pid.setKp((float) messageParser.payload / kConstantsFixedPointScaling);
      }
      messageParser.sendResponse((int) (actuator.pid.getKp() * kConstantsFixedPointScaling),
          channelParsedLength + 1);
      break;
    case kConstantsDerivativeChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.pid.setKd((float) messageParser.payload / kConstantsFixedPointScaling);
      }
      messageParser.sendResponse((int) (actuator.pid.getKd() * kConstantsFixedPointScaling),
          channelParsedLength + 1);
      break;
    case kConstantsIntegralChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.pid.setKi((float) messageParser.payload / kConstantsFixedPointScaling);
      }
      messageParser.sendResponse((int) (actuator.pid.getKi() * kConstantsFixedPointScaling),
          channelParsedLength + 1);
      break;
    case kConstantsFeedforwardChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.speedAdjuster.speedBias = messageParser.payload;
      }
      messageParser.sendResponse(actuator.speedAdjuster.speedBias, channelParsedLength + 1);
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onLimitsMessage(unsigned int channelParsedLength) {
  switch (messageParser.channel[channelParsedLength]) {
    case kLimitsPositionChannel:
      ++channelParsedLength;
      switch (messageParser.channel[channelParsedLength]) {
        case kLimitsLowerSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMinInput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMinInput(), channelParsedLength + 1);
          break;
        case kLimitsUpperSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMaxInput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMaxInput(), channelParsedLength + 1);
          break;
      }
      break;
    case kLimitsDutyChannel:
      ++channelParsedLength;
      switch (messageParser.channel[channelParsedLength]) {
        case kLimitsLowerSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMinOutput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMinOutput(), channelParsedLength + 1);
          break;
        case kLimitsUpperSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMaxOutput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMaxOutput(), channelParsedLength + 1);
          break;
      }
      break;
    case kLimitsBrakeChannel:
      ++channelParsedLength;
      switch (messageParser.channel[channelParsedLength]) {
        case kLimitsLowerSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.speedAdjuster.brakeLowerThreshold = messageParser.payload;
          }
          messageParser.sendResponse(actuator.speedAdjuster.brakeLowerThreshold, channelParsedLength + 1);
          break;
        case kLimitsUpperSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.speedAdjuster.brakeUpperThreshold = messageParser.payload;
          }
          messageParser.sendResponse(actuator.speedAdjuster.brakeUpperThreshold, channelParsedLength + 1);
          break;
      }
      break;
  }
}

template <class LinearActuatorParams>
void LinearActuatorModule<LinearActuatorParams>::onReportingMessage(unsigned int channelParsedLength) {
  switch (messageParser.channel[channelParsedLength]) {
    case kReportingConvergenceChannel:
      if (messageParser.payloadParsedLength()) {
        reportingConvergencePosition = (messageParser.payload > 0);
      }
      messageParser.sendResponse(reportingConvergencePosition, channelParsedLength + 1);
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
void LinearActuatorModule<LinearActuatorParams>::onTargetingMessage(unsigned int channelParsedLength) {
  if (messageParser.payloadParsedLength()) {
    actuator.pid.setSetpoint(messageParser.payload);
    reportedConvergence = false;
    reportedStallTimeout = false;
    actuator.unfreeze();
  }
  messageParser.sendResponse((int) actuator.pid.setpoint.current(), 2);
}

}

#endif


#ifndef LinearActuatorModule_tpp
#define LinearActuatorModule_tpp

namespace LiquidHandlingRobotics {

// LinearActuatorModule

template <class LinearActuator>
LinearActuatorModule<LinearActuator>::LinearActuatorModule(
    MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
    char actuatorChannelPrefix,
    MotorPort motorPort, uint8_t sensorId,
    int minPosition, int maxPosition,
    int minDuty, int maxDuty,
    double pidKp, double pidKd, double pidKi,
    int pidSampleTime,
    int feedforward,
    int brakeLowerThreshold, int brakeUpperThreshold,
    bool swapMotorPolarity,
    int convergenceDelay,
    int stallTimeout, float stallSmootherSnapMultiplier, int stallSmootherMax,
    bool stallSmootherEnableSleep, float stallSmootherActivityThreshold
) :
  messageParser(messageParser),
  actuator(
    motors, motorPort,
    sensorId, minPosition, maxPosition,
    pidKp, pidKd, pidKi, pidSampleTime,
    swapMotorPolarity, feedforward,
    brakeLowerThreshold, brakeUpperThreshold,
    minDuty, maxDuty
  ),
  smoother(
      actuator.position,
      stallSmootherSnapMultiplier, stallSmootherMax,
      stallSmootherEnableSleep, stallSmootherActivityThreshold
  ),
  moduleChannel(actuatorChannelPrefix),
  convergenceDelay(convergenceDelay), stallTimeout(stallTimeout)
{}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::setup() {
  if (setupCompleted) return;

  actuator.setup();
  smoother.setup();

  state.setup(State::ready);

  setupCompleted = true;
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::update() {
  actuator.update();
  smoother.update();

  if (messageParser.justReceived() && messageParser.channel[0] == moduleChannel) {
    onReceivedMessage(1);
  }

  switch (state.current()) {
    case State::ready:
      if (reportingConvergencePosition &&
          !reportedConvergence) reportPosition(kReportingConvergenceChannel);
    case State::pidTargeting:
      if (converged(convergenceDelay)) {
        actuator.freeze(true);
        state.update(State::dutyControl, true);
        if (reportingConvergencePosition &&
            !reportedConvergence) reportPosition(kReportingConvergenceChannel);
      } else if (stalled(stallTimeout)) {
        actuator.freeze(true);
        state.update(State::dutyControl, true);
        if (reportingStallTimeoutPosition && !reportedConvergence &&
            !reportedStallTimeout) reportPosition(kReportingStallTimeoutChannel);
      }
      break;
    case State::dutyControl:
      if (stopped(convergenceDelay) &&
          reportingConvergencePosition &&
          !reportedConvergence &&
          !reportedStallTimeout) reportPosition(kReportingConvergenceChannel);
      else if (stalled(stallTimeout) &&
          reportingStallTimeoutPosition &&
          !reportedStallTimeout) {
        actuator.freeze(true);
        reportPosition(kReportingStallTimeoutChannel);
      }
      break;
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

template <class LinearActuator>
bool LinearActuatorModule<LinearActuator>::converged(unsigned int convergenceTime) const {
  if (!convergenceTime) convergenceTime = convergenceDelay;
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime) &&
    state.settled(convergenceTime);
}

template <class LinearActuator>
bool LinearActuatorModule<LinearActuator>::stalled(unsigned int stallTime) const {
  if (!stallTime) stallTime = stallTimeout;
  return actuator.motor.speed != 0 &&
    actuator.pid.setpoint.settled(stallTime) &&
    smoother.output.settled(stallTime) &&
    state.settled(stallTime);
}

template <class LinearActuator>
bool LinearActuatorModule<LinearActuator>::stopped(unsigned int convergenceTime) const {
  if (!convergenceTime) convergenceTime = convergenceDelay;
  return actuator.motor.speed == 0 &&
    smoother.output.settled(convergenceTime) &&
    state.settled(convergenceTime);
}

template<class LinearActuator>
void LinearActuatorModule<LinearActuator>::targetPosition(Position position) {
    actuator.pid.setSetpoint(position);
    reportedConvergence = false;
    reportedStallTimeout = false;
    state.update(State::pidTargeting, true);
    actuator.unfreeze();
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::reportPosition(char reportingChannel) {
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

template<class LinearActuator>
void LinearActuatorModule<LinearActuator>::setDirectDuty(int duty) {
    reportedConvergence = false;
    reportedStallTimeout = false;
    state.update(State::dutyControl, true);
    actuator.freeze(true);
    actuator.motor.run(constrain(duty, -255, 255));
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::onReceivedMessage(unsigned int channelParsedLength) {
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
    case kDutyChannel:
      onDutyMessage(channelParsedLength + 1);
      break;
  }
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::onConstantsMessage(unsigned int channelParsedLength) {
  if (messageParser.channelParsedLength() != channelParsedLength + 1) return;
  switch (messageParser.channel[channelParsedLength]) {
    case kConstantsProportionalChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.pid.setKp((float) messageParser.payload / kConstantsFixedPointScaling);
      }
      messageParser.sendResponse((int) (actuator.pid.getKp() * kConstantsFixedPointScaling));
      break;
    case kConstantsDerivativeChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.pid.setKd((float) messageParser.payload / kConstantsFixedPointScaling);
      }
      messageParser.sendResponse((int) (actuator.pid.getKd() * kConstantsFixedPointScaling));
      break;
    case kConstantsIntegralChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.pid.setKi((float) messageParser.payload / kConstantsFixedPointScaling);
      }
      messageParser.sendResponse((int) (actuator.pid.getKi() * kConstantsFixedPointScaling));
      break;
    case kConstantsFeedforwardChannel:
      if (messageParser.payloadParsedLength()) {
        actuator.speedAdjuster.speedBias = messageParser.payload;
      }
      messageParser.sendResponse(actuator.speedAdjuster.speedBias);
      break;
  }
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::onLimitsMessage(unsigned int channelParsedLength) {
  if (messageParser.channelParsedLength() != channelParsedLength + 2) return;
  switch (messageParser.channel[channelParsedLength]) {
    case kLimitsPositionChannel:
      switch (messageParser.channel[channelParsedLength + 1]) {
        case kLimitsLowerSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMinInput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMinInput());
          break;
        case kLimitsUpperSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMaxInput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMaxInput());
          break;
      }
      break;
    case kLimitsDutyChannel:
      switch (messageParser.channel[channelParsedLength + 1]) {
        case kLimitsLowerSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMinOutput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMinOutput());
          break;
        case kLimitsUpperSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.pid.setMaxOutput(messageParser.payload);
          }
          messageParser.sendResponse(actuator.pid.getMaxOutput());
          break;
      }
      break;
    case kLimitsBrakeChannel:
      switch (messageParser.channel[channelParsedLength + 1]) {
        case kLimitsLowerSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.speedAdjuster.brakeLowerThreshold = messageParser.payload;
          }
          messageParser.sendResponse(actuator.speedAdjuster.brakeLowerThreshold);
          break;
        case kLimitsUpperSubchannel:
          if (messageParser.payloadParsedLength()) {
            actuator.speedAdjuster.brakeUpperThreshold = messageParser.payload;
          }
          messageParser.sendResponse(actuator.speedAdjuster.brakeUpperThreshold);
          break;
      }
      break;
  }
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::onReportingMessage(unsigned int channelParsedLength) {
  if (messageParser.channelParsedLength() != channelParsedLength + 1) return;
  switch (messageParser.channel[channelParsedLength]) {
    case kReportingConvergenceChannel:
      if (messageParser.payloadParsedLength()) {
        reportingConvergencePosition = (messageParser.payload > 0);
      }
      messageParser.sendResponse(reportingConvergencePosition);
      break;
    case kReportingStallTimeoutChannel:
      if (messageParser.payloadParsedLength()) {
        reportingStallTimeoutPosition = (messageParser.payload > 0);
      }
      messageParser.sendResponse(reportingStallTimeoutPosition);
      break;
    case kReportingStreamingChannel:
      if (!messageParser.payloadParsedLength()) break;
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

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::onTargetingMessage(unsigned int channelParsedLength) {
  if (messageParser.channelParsedLength() != channelParsedLength) return;
  if (messageParser.payloadParsedLength()) targetPosition(messageParser.payload);
  messageParser.sendResponse((int) actuator.pid.setpoint.current());
}

template <class LinearActuator>
void LinearActuatorModule<LinearActuator>::onDutyMessage(unsigned int channelParsedLength) {
  if (messageParser.channelParsedLength() != channelParsedLength) return;
  if (messageParser.payloadParsedLength()) setDirectDuty(messageParser.payload);
  messageParser.sendResponse(actuator.motor.speed);
}

}

#endif


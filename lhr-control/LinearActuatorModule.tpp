#ifndef LinearActuatorModule_tpp
#define LinearActuatorModule_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

// LinearActuatorModule

template <class LinearActuator, class Messager>
LinearActuatorModule<LinearActuator, Messager>::LinearActuatorModule(
    Messager &messager,
    LinearPositionControl::Components::Motors &motors,
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
  messager(messager),
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

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::setup() {
  if (setupCompleted) return;

  actuator.setup();
  smoother.setup();

  state.setup(State::ready);

  setupCompleted = true;
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::update() {
  wdt_reset();
  actuator.update();
  wdt_reset();
  smoother.update();

  if (messager.parser.justReceived() && messager.parser.channel[0] == moduleChannel) {
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

  wdt_reset();
  if (streamingPositionReportInterval > 0) {
    if (streamingPositionClock == 0) reportPosition(kReportingStreamingChannel);
    streamingPositionClock = (streamingPositionClock + 1) % streamingPositionReportInterval;
  }

  wdt_reset();
  if (queryPositionCountdown > 0) {
    reportPosition(kReportingQueryChannel);
    --queryPositionCountdown;
  }

  wdt_reset();
}

template <class LinearActuator, class Messager>
bool LinearActuatorModule<LinearActuator, Messager>::converged(unsigned int convergenceTime) const {
  if (!convergenceTime) convergenceTime = convergenceDelay;
  return actuator.pid.setpoint.settled(convergenceTime) &&
    actuator.speedAdjuster.output.settledAt(0, convergenceTime) &&
    state.settled(convergenceTime);
}

template <class LinearActuator, class Messager>
bool LinearActuatorModule<LinearActuator, Messager>::stalled(unsigned int stallTime) const {
  if (!stallTime) stallTime = stallTimeout;
  return actuator.motor.speed != 0 &&
    actuator.pid.setpoint.settled(stallTime) &&
    smoother.output.settled(stallTime) &&
    state.settled(stallTime);
}

template <class LinearActuator, class Messager>
bool LinearActuatorModule<LinearActuator, Messager>::stopped(unsigned int convergenceTime) const {
  if (!convergenceTime) convergenceTime = convergenceDelay;
  return actuator.motor.speed == 0 &&
    smoother.output.settled(convergenceTime) &&
    state.settled(convergenceTime);
}

template<class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::targetPosition(Position position) {
    actuator.pid.setSetpoint(position);
    reportedConvergence = false;
    reportedStallTimeout = false;
    state.update(State::pidTargeting, true);
    actuator.unfreeze();
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::reportPosition(char reportingChannel) {
  messager.sender.sendChannelStart();
  messager.sender.sendChannelChar(moduleChannel);
  messager.sender.sendChannelChar(kReportingChannel);
  messager.sender.sendChannelChar(reportingChannel);
  messager.sender.sendChannelEnd();
  messager.sender.sendPayload(actuator.position.current());
  switch (reportingChannel) {
    case kReportingConvergenceChannel:
      reportedConvergence = true;
      break;
    case kReportingStallTimeoutChannel:
      reportedStallTimeout = true;
      break;
  }
}

template<class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::setDirectDuty(int duty) {
    reportedConvergence = false;
    reportedStallTimeout = false;
    state.update(State::dutyControl, true);
    actuator.freeze(true);
    actuator.motor.run(constrain(duty, -255, 255));
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::onReceivedMessage(unsigned int channelParsedLength) {
  switch (messager.parser.channel[channelParsedLength]) {
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

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::onConstantsMessage(unsigned int channelParsedLength) {
  if (messager.parser.channelParsedLength() != channelParsedLength + 1) return;
  switch (messager.parser.channel[channelParsedLength]) {
    case kConstantsProportionalChannel:
      if (messager.parser.payloadParsedLength()) {
        actuator.pid.setKp((float) messager.parser.payload / kConstantsFixedPointScaling);
      }
      messager.sendResponse((int) (actuator.pid.getKp() * kConstantsFixedPointScaling));
      break;
    case kConstantsDerivativeChannel:
      if (messager.parser.payloadParsedLength()) {
        actuator.pid.setKd((float) messager.parser.payload / kConstantsFixedPointScaling);
      }
      messager.sendResponse((int) (actuator.pid.getKd() * kConstantsFixedPointScaling));
      break;
    case kConstantsIntegralChannel:
      if (messager.parser.payloadParsedLength()) {
        actuator.pid.setKi((float) messager.parser.payload / kConstantsFixedPointScaling);
      }
      messager.sendResponse((int) (actuator.pid.getKi() * kConstantsFixedPointScaling));
      break;
    case kConstantsFeedforwardChannel:
      if (messager.parser.payloadParsedLength()) {
        actuator.speedAdjuster.speedBias = constrain(messager.parser.payload, -255 * 2, 255 * 2);
      }
      messager.sendResponse(actuator.speedAdjuster.speedBias);
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::onLimitsMessage(unsigned int channelParsedLength) {
  if (messager.parser.channelParsedLength() != channelParsedLength + 2) return;
  switch (messager.parser.channel[channelParsedLength]) {
    case kLimitsPositionChannel:
      switch (messager.parser.channel[channelParsedLength + 1]) {
        case kLimitsLowerSubchannel:
          if (messager.parser.payloadParsedLength() &&
              messager.parser.payload <= actuator.pid.getMaxInput()) {
            actuator.pid.setMinInput(messager.parser.payload);
          }
          messager.sendResponse(actuator.pid.getMinInput());
          break;
        case kLimitsUpperSubchannel:
          if (messager.parser.payloadParsedLength() &&
              messager.parser.payload >= actuator.pid.getMinInput()) {
            actuator.pid.setMaxInput(messager.parser.payload);
          }
          messager.sendResponse(actuator.pid.getMaxInput());
          break;
      }
      break;
    case kLimitsDutyChannel:
      switch (messager.parser.channel[channelParsedLength + 1]) {
        case kLimitsLowerSubchannel:
          if (messager.parser.payloadParsedLength()) {
            actuator.pid.setMinOutput(constrain(messager.parser.payload, -255, 255));
          }
          messager.sendResponse(actuator.pid.getMinOutput());
          break;
        case kLimitsUpperSubchannel:
          if (messager.parser.payloadParsedLength()) {
            actuator.pid.setMaxOutput(constrain(messager.parser.payload, -255, 255));
          }
          messager.sendResponse(actuator.pid.getMaxOutput());
          break;
      }
      break;
    case kLimitsBrakeChannel:
      switch (messager.parser.channel[channelParsedLength + 1]) {
        case kLimitsLowerSubchannel:
          if (messager.parser.payloadParsedLength()) {
            actuator.speedAdjuster.brakeLowerThreshold = constrain(messager.parser.payload, -255, 255);
          }
          messager.sendResponse(actuator.speedAdjuster.brakeLowerThreshold);
          break;
        case kLimitsUpperSubchannel:
          if (messager.parser.payloadParsedLength()) {
            actuator.speedAdjuster.brakeUpperThreshold = constrain(messager.parser.payload, -255, 255);
          }
          messager.sendResponse(actuator.speedAdjuster.brakeUpperThreshold);
          break;
      }
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::onReportingMessage(unsigned int channelParsedLength) {
  if (messager.parser.channelParsedLength() != channelParsedLength + 1) return;
  switch (messager.parser.channel[channelParsedLength]) {
    case kReportingConvergenceChannel:
      if (messager.parser.payloadParsedLength()) {
        reportingConvergencePosition = (messager.parser.payload > 0);
      }
      messager.sendResponse(reportingConvergencePosition);
      break;
    case kReportingStallTimeoutChannel:
      if (messager.parser.payloadParsedLength()) {
        reportingStallTimeoutPosition = (messager.parser.payload > 0);
      }
      messager.sendResponse(reportingStallTimeoutPosition);
      break;
    case kReportingStreamingChannel:
      if (!messager.parser.payloadParsedLength()) break;
      reportPosition(kReportingStreamingChannel);
      streamingPositionReportInterval = max(messager.parser.payload, 0);
      streamingPositionClock = 0;
      break;
    case kReportingQueryChannel:
      reportPosition(kReportingQueryChannel);
      queryPositionCountdown = max(messager.parser.payload, 0);
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::onTargetingMessage(unsigned int channelParsedLength) {
  if (messager.parser.channelParsedLength() != channelParsedLength) return;
  if (messager.parser.payloadParsedLength()) targetPosition(messager.parser.payload);
  messager.sendResponse((int) actuator.pid.setpoint.current());
}

template <class LinearActuator, class Messager>
void LinearActuatorModule<LinearActuator, Messager>::onDutyMessage(unsigned int channelParsedLength) {
  if (messager.parser.channelParsedLength() != channelParsedLength) return;
  if (messager.parser.payloadParsedLength()) setDirectDuty(messager.parser.payload);
  messager.sendResponse(actuator.motor.speed);
}

}

#endif


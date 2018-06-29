#ifndef LinearActuatorAxis_tpp
#define LinearActuatorAxis_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics { namespace Protocol {

// Notifier

template <class Messager, class SignalType>
Notifier<Messager, SignalType>::Notifier(
    Messager &messager, const SignalType &signalValue,
    char axisChannel, char signalChannel
) :
  messager(messager), parser(messager.parser), sender(messager.sender),
  signalValue(signalValue),
  axisChannel(axisChannel), signalChannel(signalChannel)
{}

template <class Messager, class SignalType>
void Notifier<Messager, SignalType>::update() {
  using namespace Channels::LinearActuator;

  if ((parser.justReceived() && parser.channelParsedLength >= 3 &&
        parser.channel[0] == axisChannel &&
        parser.channel[1] == signalChannel &&
        parser.channel[2] == kNotify)) { // parsed as: _*n
    onReceivedMessage();
  }
  if (state == State::silent) return;

  switch (state) {
    case State::iterationIntervals:
      iteration = (iteration + 1) % interval;
      if (iteration != 0) return;
      break;
    case State::timeIntervals:
      if (timer < interval) return;
      timer = 0;
      break;
    default:
      return;
  }

  if (changeOnly && signalValue == prevSignalValue) return;
  prevSignalValue = signalValue;

  if (number == 0) {
    number = -1;
    notifyNumber();
    state = State::silent;
    notifyState();
    return;
  }
  notify();
  if (number > 0) --number;
}

template <class Messager, class SignalType>
void Notifier<Messager, SignalType>::notifyIterationIntervals(unsigned int interval) {
  state = State::iterationIntervals;
  interval = max(1, interval);
  notify();
  iteration = 0;
}

template <class Messager, class SignalType>
void Notifier<Messager, SignalType>::notifyTimeIntervals(unsigned int interval) {
  state = State::timeIntervals;
  interval = max(1, interval);
  notify();
  timer = 0;
}

template <class Messager, class SignalType>
void Notifier<Messager, SignalType>::notify() {
  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(signalChannel);
  sender.sendChannelEnd();
  sender.sendPayload(static_cast<int>(signalValue));
}

template<class Messager, class SignalType>
void Notifier<Messager, SignalType>::notifyNumber() {
  using namespace Channels::LinearActuator;
  using namespace Channels::LinearActuator::Notify;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(signalChannel);
  sender.sendChannelChar(kNotify);
  sender.sendChannelChar(kNumber);
  sender.sendChannelEnd();
  sender.sendPayload(number);
}
template<class Messager, class SignalType>
void Notifier<Messager, SignalType>::notifyState() {
  using namespace Channels::LinearActuator;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(signalChannel);
  sender.sendChannelChar(kNotify);
  sender.sendChannelEnd();
  sender.sendPayload(static_cast<int>(state));
}


template <class Messager, class SignalType>
void Notifier<Messager, SignalType>::onReceivedMessage() {
  using namespace Channels::LinearActuator;
  using namespace Channels::LinearActuator::Notify;

  uint8_t channelLength = messager.parser.channelParsedLength;

  if (channelLength == 3 && messager.parser.channel[2] == kNotify) { // parsed as: _*n
    if (parser.receivedPayload()) {
      switch (messager.parser.payload) {
        case 0:
          state = State::silent;
          break;
        case 1:
          state = State::iterationIntervals;
          if (changeOnly) prevSignalValue = signalValue - 1;
          break;
        case 2:
          state = State::timeIntervals;
          if (changeOnly) prevSignalValue = signalValue - 1;
          break;
      }
    }
    messager.sendResponse(static_cast<int>(state));
    return;
  }
  if (channelLength == 4) {
    switch (messager.parser.channel[3]) {
      case kInterval: // parsed as: _*ni
        if (parser.receivedPayload() && messager.parser.payload > 0) {
          interval = messager.parser.payload;
        }
        messager.sendResponse(static_cast<int>(interval));
        break;
      case kChangeOnly: // parsed as: _*nc
        if (parser.receivedPayload()) {
          if (messager.parser.payload == 1) changeOnly = true;
          else if (messager.parser.payload == 0) changeOnly = false;
        }
        messager.sendResponse(changeOnly);
        break;
      case kNumber: // parsed as: _*nn
        if (parser.receivedPayload()) number = messager.parser.payload;
        messager.sendResponse(number);
        break;
    }
  }
}

// LinearActuatorAxis

template <class LinearActuator, class Messager>
LinearActuatorAxis<LinearActuator, Messager>::LinearActuatorAxis(
    Messager &messager,
    LinearPositionControl::Components::Motors &motors,
    char axisChannel,
    MotorPort motorPort, uint8_t sensorId,
    int minPosition, int maxPosition,
    int minDuty, int maxDuty,
    double pidKp, double pidKd, double pidKi, int pidSampleTime,
    int feedforward,
    int brakeLowerThreshold, int brakeUpperThreshold,
    bool swapMotorPolarity,
    int convergenceTimeout, int stallTimeout, int timerTimeout,
    float smootherSnapMultiplier, int smootherMax,
    bool smootherEnableSleep, float smootherActivityThreshold
) :
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
      smootherSnapMultiplier, smootherMax,
      smootherEnableSleep, smootherActivityThreshold
  ),
  convergenceTimeout(convergenceTimeout), stallTimeout(stallTimeout),
  timerTimeout(timerTimeout),
  messager(messager), parser(messager.parser), sender(messager.sender),
  axisChannel(axisChannel),
  positionNotifier(
      messager, actuator.position.current,
      axisChannel, Channels::LinearActuator::kPosition
  ),
  /* smoothedPositionNotifier( */
  /*     messager, smoother.output.current, */
  /*     axisChannel, Channels::LinearActuator::kSmoothedPosition */
  /* ), */
  motorDutyNotifier(
      messager, actuator.motor.speed,
      axisChannel, Channels::LinearActuator::kMotor
  )
{}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::setup() {
  if (setupCompleted) return;

  actuator.setup();
  smoother.setup();

  state.setup(State::directMotorDutyIdle);

  setupCompleted = true;
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::update() {
  wdt_reset();
  actuator.update();
  wdt_reset();
  smoother.update();
  wdt_reset();

  if (parser.justReceived() && parser.channelParsedLength > 0 &&
      parser.channel[0] == axisChannel) {
    onReceivedMessage(1);
  }
  wdt_reset();
  positionNotifier.update();
  /* wdt_reset(); */
  /* smoothedPositionNotifier.update(); */
  wdt_reset();
  motorDutyNotifier.update();
  wdt_reset();

  switch (state.current) {
    case State::directMotorDutyControl:
      if (stalled()) endControl(State::stallTimeoutStopped);
      else if (timed()) endControl(State::timerTimeoutStopped);
      break;
    case State::positionFeedbackControl:
      if (converged()) endControl(State::convergenceTimeoutStopped);
      else if (stalled()) endControl(State::stallTimeoutStopped);
      break;
  }

  wdt_reset();
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onConnect() {
  allowNotifications = true;
  notifyState();
  notifyPosition();
  notifyMotor();
}

template <class LinearActuator, class Messager>
bool LinearActuatorAxis<LinearActuator, Messager>::converged() const {
  return (
      convergenceTimeout > 0 &&
      state.settledAt(State::positionFeedbackControl, convergenceTimeout) &&
      actuator.pid.setpoint.settled(convergenceTimeout) &&
      actuator.speedAdjuster.output.settledAt(0, convergenceTimeout)
  );
}

template <class LinearActuator, class Messager>
bool LinearActuatorAxis<LinearActuator, Messager>::stalled() const {
  return (
      stallTimeout > 0 &&
      state.settled(stallTimeout) &&
      (
       (state.at(State::directMotorDutyControl) && actuator.motor.speed != 0) ||
       (state.at(State::positionFeedbackControl) &&
        actuator.pid.setpoint.settled(stallTimeout) &&
        !actuator.speedAdjuster.output.settledAt(0, stallTimeout)
       )
      ) &&
      smoother.output.settled(stallTimeout)
  );
}

template <class LinearActuator, class Messager>
bool LinearActuatorAxis<LinearActuator, Messager>::timed() const {
  return timerTimeout > 0 && state.settled(timerTimeout);
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::startPositionFeedbackControl(Position setpoint) {
  actuator.pid.setSetpoint(setpoint);
  state.update(State::positionFeedbackControl, true);
  actuator.unfreeze();
  notifyFeedbackControllerSetpoint();
  notifyState();
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::startDirectMotorDutyControl(int duty) {
  if (duty == 0) state.update(State::directMotorDutyIdle, true);
  else state.update(State::directMotorDutyControl, true);
  actuator.freeze(true);
  actuator.motor.run(constrain(duty, -255, 255));
  notifyMotor();
  notifyState();
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::endControl(State nextState) {
  if (nextState == State::directMotorDutyIdle ||
      nextState == State::directMotorDutyControl ||
      nextState == State::positionFeedbackControl) return;
  actuator.freeze(true);
  actuator.motor.run(0);
  notifyPosition();
  switch (state.current) {
    case State::directMotorDutyControl:
      notifyMotor();
      break;
    case State::positionFeedbackControl:
      notifyFeedbackControllerSetpoint();
      break;
  }
  state.update(nextState);
  notifyState();
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::notifyPosition() {
  using namespace Channels::LinearActuator;

  if (!allowNotifications) return;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(kPosition);
  sender.sendChannelEnd();
  sender.sendPayload(static_cast<int>(actuator.position.current));
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::notifySmoothedPosition() {
  using namespace Channels::LinearActuator;

  if (!allowNotifications) return;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(kSmoothedPosition);
  sender.sendChannelEnd();
  sender.sendPayload(static_cast<int>(smoother.output.current));
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::notifyMotor() {
  using namespace Channels::LinearActuator;

  if (!allowNotifications) return;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(kMotor);
  sender.sendChannelEnd();
  sender.sendPayload(actuator.motor.speed);
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::notifyState() {
  if (!allowNotifications) return;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelEnd();
  sender.sendPayload(static_cast<int>(state.current));
}

template<class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::notifyFeedbackControllerSetpoint() {
  using namespace Channels::LinearActuator;

  if (!allowNotifications) return;

  sender.sendChannelStart();
  sender.sendChannelChar(axisChannel);
  sender.sendChannelChar(kFeedbackController);
  sender.sendChannelEnd();
  sender.sendPayload(static_cast<int>(actuator.pid.setpoint.current));
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onReceivedMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 1
  // Expects previously parsed: _
  uint8_t channelLength = parser.channelParsedLength;

  if (channelLength == channelParsedLength) { // parsed as: _
    messager.sendResponse(static_cast<int>(state.current));
    return;
  }

  switch (parser.channel[channelParsedLength]) {
    case kPosition: // parsed as: _p
      onPositionMessage(channelParsedLength + 1);
      break;
    case kSmoothedPosition: // parsed as: _s
      onSmoothedPositionMessage(channelParsedLength + 1);
      break;
    case kMotor: // parsed as: _m
      onMotorMessage(channelParsedLength + 1);
      break;
    case kFeedbackController: // parsed as: _f
      onFeedbackControllerMessage(channelParsedLength + 1);
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onPositionMessage(
    unsigned int channelParsedLength
) {
  // Expects parser.justReceived()
  // Expects channelParsedLength == 2
  // Expects previously parsed: _p
  uint8_t channelLength = parser.channelParsedLength;

  if (channelLength == channelParsedLength) { // parsed as: _p
    notifyPosition();
    return;
  }

  // Messages on LinearActuator/Position/Notify are handled separately
  // by positionNotifier.update()
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onSmoothedPositionMessage(
    unsigned int channelParsedLength
) {
  // Expects parser.justReceived()
  // Expects channelParsedLength == 2
  // Expects previously parsed: _s
  uint8_t channelLength = parser.channelParsedLength;

  if (channelLength == channelParsedLength) { // parsed as: _s
    notifySmoothedPosition();
    return;
  }

  // Messages on LinearActuator/SmoothedPosition/Notify are handled separately
  // by smoothedPositionNotifier.update()

  // TODO: implement protocol and command handlers for other child channels
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onMotorMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator::Motor;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 2
  // Expects previously parsed: _m
  uint8_t channelLength = parser.channelParsedLength;
  int payload = parser.payload;

  if (channelLength == channelParsedLength) { // parsed as: _m
    if (parser.receivedPayload()) startDirectMotorDutyControl(parser.payload);
    else notifyMotor();
    return;
  }

  // Messages on LinearActuator/Motor/Notify are handled separately
  // by smoothedPositionNotifier.update()

  if (channelLength == channelParsedLength + 1) {
    switch (parser.channel[channelParsedLength]) {
      case kStallProtectorTimeout: // parsed as: _ms
        if (parser.receivedPayload() && payload >= 0) stallTimeout = payload;
        messager.sendResponse(stallTimeout);
        break;
      case kTimerTimeout: // parsed as: _mt
        if (parser.receivedPayload() && payload >= 0) timerTimeout = payload;
        messager.sendResponse(timerTimeout);
        break;
      case kPolarity: // parsed as: _mp
        if (parser.receivedPayload() &&
            (payload == -1 && !actuator.motor.directionsSwapped()) ||
            (payload == 1 && actuator.motor.directionsSwapped())) {
          actuator.motor.swapDirections();
        }
        messager.sendResponse((actuator.motor.directionsSwapped()) ? -1 : 1);
        break;
    }
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onFeedbackControllerMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator::FeedbackController;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 2
  // Expects previously parsed: _f
  uint8_t channelLength = parser.channelParsedLength;
  int payload = parser.payload;

  if (channelLength == channelParsedLength) { // parsed as: _f
    if (parser.receivedPayload()) startPositionFeedbackControl(parser.payload);
    else notifyFeedbackControllerSetpoint();
    return;
  }

  // Expects channelLength >= 3
  if (channelLength == channelParsedLength + 1) {
    switch (parser.channel[channelParsedLength]) {
      case kConvergenceTimeout: // parsed as: _fc
        if (parser.receivedPayload() && payload >= 0) convergenceTimeout = payload;
        messager.sendResponse(convergenceTimeout);
        break;
    }
    return;
  }

  // Expects channelLength > 3
  switch (parser.channel[channelParsedLength]) {
    case kLimits: // parsed as: _fl
      onFeedbackControllerLimitsMessage(channelParsedLength + 1);
      break;
    case kPID: // parsed as: _fp
      onFeedbackControllerPIDMessage(channelParsedLength + 1);
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onFeedbackControllerLimitsMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 3
  // Expects previously parsed: _fl
  uint8_t channelLength = parser.channelParsedLength;
  int payload = parser.payload;

  if (channelLength < channelParsedLength + 2) return;

  // Expects channelLength >= 5
  switch (parser.channel[channelParsedLength]) {
    case kPosition: // parsed as: _flp
      onFeedbackControllerLimitsPositionMessage(channelParsedLength + 1);
      break;
    case kMotor: // parsed as: _flm
      onFeedbackControllerLimitsMotorMessage(channelParsedLength + 1);
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onFeedbackControllerLimitsPositionMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator::FeedbackController;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 4
  // Expects previously parsed: _flp
  uint8_t channelLength = parser.channelParsedLength;
  int payload = parser.payload;

  if (channelLength != channelParsedLength + 1) return;

  // Expects channelLength == 5
  switch (parser.channel[channelParsedLength]) {
    case Limits::kLow: // parsed as: _flpl
      if (parser.receivedPayload() && parser.payload <= actuator.pid.getMaxInput()) {
        actuator.pid.setMinInput(parser.payload);
      }
      messager.sendResponse(actuator.pid.getMinInput());
      break;
    case Limits::kHigh: // parsed as: _flph
      if (parser.receivedPayload() && parser.payload >= actuator.pid.getMinInput()) {
        actuator.pid.setMaxInput(parser.payload);
      }
      messager.sendResponse(actuator.pid.getMaxInput());
      break;
  }
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onFeedbackControllerLimitsMotorMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator;
  using namespace Channels::LinearActuator::FeedbackController;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 4
  // Expects previously parsed: _flm
  uint8_t channelLength = parser.channelParsedLength;
  int payload = parser.payload;

  if (channelLength != channelParsedLength + 2) return;

  // Expects channelLength == 6
  switch (parser.channel[channelParsedLength]) {
    case Limits::Motor::kForwards: // parsed as: _flmf
      switch (parser.channel[channelParsedLength + 1]) {
        case Limits::kHigh: // parsed as: _flmh
          if (parser.receivedPayload() &&
              parser.payload <= 255 &&
              parser.payload >= actuator.speedAdjuster.brakeUpperThreshold) {
            actuator.pid.setMaxOutput(parser.payload);
          }
          messager.sendResponse(actuator.pid.getMaxOutput());
          break;
        case Limits::kLow: // parsed as: _flml
          if (parser.receivedPayload() &&
              parser.payload <= actuator.pid.getMaxOutput() &&
              parser.payload >= actuator.speedAdjuster.brakeLowerThreshold) {
            actuator.speedAdjuster.brakeUpperThreshold = parser.payload;
          }
          messager.sendResponse(actuator.speedAdjuster.brakeUpperThreshold);
          break;
      }
      break;
    case Limits::Motor::kBackwards: // parsed as: _flmb
      switch (parser.channel[channelParsedLength + 1]) {
        case Limits::kLow: // parsed as: _flml
          if (parser.receivedPayload() &&
              parser.payload <= actuator.speedAdjuster.brakeUpperThreshold &&
              parser.payload >= actuator.pid.getMinOutput()) {
            actuator.speedAdjuster.brakeLowerThreshold = parser.payload;
          }
          messager.sendResponse(actuator.speedAdjuster.brakeLowerThreshold);
          break;
        case Limits::kHigh: // parsed as: _flmh
          if (parser.receivedPayload() &&
              parser.payload <= actuator.speedAdjuster.brakeLowerThreshold &&
              parser.payload >= -255) {
            actuator.pid.setMinOutput(parser.payload);
          }
          messager.sendResponse(actuator.pid.getMinOutput());
          break;
      }
      break;
  }
}

inline float fixedPointToFloat(int fixedPointNum) {
  return static_cast<float>(fixedPointNum) / kConstantsFixedPointScaling;
}

inline float floatToFixedPoint(float floatNum) {
  return static_cast<int>(floatNum * kConstantsFixedPointScaling);
}

template <class LinearActuator, class Messager>
void LinearActuatorAxis<LinearActuator, Messager>::onFeedbackControllerPIDMessage(
    unsigned int channelParsedLength
) {
  using namespace Channels::LinearActuator::FeedbackController::PID;

  // Expects parser.justReceived()
  // Expects channelParsedLength == 3
  // Expects previously parsed: _fp
  uint8_t channelLength = parser.channelParsedLength;
  int payload = parser.payload;

  if (channelLength != channelParsedLength + 1) return;

  // Expects channelLength == 4
  switch (parser.channel[channelParsedLength]) {
    case kKp:
      if (parser.receivedPayload()) actuator.pid.setKp(fixedPointToFloat(parser.payload));
      messager.sendResponse(floatToFixedPoint(actuator.pid.getKp()));
      break;
    case kKd:
      if (parser.receivedPayload()) actuator.pid.setKd(fixedPointToFloat(parser.payload));
      messager.sendResponse(floatToFixedPoint(actuator.pid.getKd()));
      break;
    case kKi:
      if (parser.receivedPayload()) actuator.pid.setKi(fixedPointToFloat(parser.payload));
      messager.sendResponse(floatToFixedPoint(actuator.pid.getKi()));
      break;
    case kSampleInterval:
      if (parser.receivedPayload() && parser.payload > 0) actuator.pid.setSampleTime(parser.payload);
      messager.sendResponse(actuator.pid.getSampleTime());
      break;
  }
  return;
}

} }

#endif


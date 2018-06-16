#ifndef CoreProtocol_tpp
#define CoreProtocol_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

void hardReset() {
  wdt_enable(static_cast<uint8_t>(WatchdogTimeout::to15ms));
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

// CoreProtocol

template<class Messager>
CoreProtocol<Messager>::CoreProtocol(Messager &messager) :
  led(LED_BUILTIN), messager(messager),
  parser(messager.parser), sender(messager.sender)
{}

template<class Messager>
void CoreProtocol<Messager>::setup() {
  if (setupCompleted) return;

  wdt_disable();
  led.setup();

  setupCompleted = true;
}

template<class Messager>
void CoreProtocol<Messager>::update() {
  wdt_reset();
  handleResetCommand();
  wdt_reset();
  handleVersionCommand();
  wdt_reset();
  handleEchoCommand();
  wdt_reset();
  handleIOCommand();
  wdt_reset();
  handleBuiltinLEDCommand();
  led.update();
  if (reportBlinkUpdates && !led.state.justEntered(previousLEDState) &&
      (led.state.justEntered(LED::State::blinkingHigh) ||
        led.state.justEntered(LED::State::blinkingLow))) {
    sendBuiltinLEDState();
  }
  previousLEDState = led.state.current();
  wdt_reset();
  if (led.state.current() == LED::State::off && led.periods == 0 && !reportedBlinkEnd &&
      (led.state.previous() == LED::State::blinkingHigh ||
       led.state.previous() == LED::State::blinkingLow)) {
    led.periods = -1;
    reportedBlinkEnd = true;
    sendBuiltinLEDBlinkState();
    sendBuiltinLEDBlinkPeriods();
  }
  wdt_reset();
}

template<class Messager>
void CoreProtocol<Messager>::onConnect(WatchdogTimeout timeout) {
  sendAllVersionMessages();
  wdt_enable(static_cast<uint8_t>(timeout));
}

template<class Messager>
void CoreProtocol<Messager>::sendVersionMessage(char versionPosition) {
  int channelPosition = versionPosition - '0';
  if (channelPosition < 0 || channelPosition >= 3) return;
  sender.sendChannelStart();
  sender.sendChannelChar(kVersionChannel);
  sender.sendChannelChar(versionPosition);
  sender.sendChannelEnd();
  sender.sendPayload((int) pgm_read_word_near(kVersion + channelPosition));
}

template<class Messager>
void CoreProtocol<Messager>::sendAllVersionMessages() {
  sendVersionMessage('0');
  wdt_reset();
  sendVersionMessage('1');
  wdt_reset();
  sendVersionMessage('2');
  wdt_reset();
}

template<class Messager>
void CoreProtocol<Messager>::handleResetCommand() {
  if (!(parser.justReceived() && parser.channel[0] == kResetChannel &&
        parser.channelParsedLength() == 1)) return;
  bool reset = false;
  sender.sendChannelStart();
  sender.sendChannelChar(kResetChannel);
  sender.sendChannelEnd();
  reset = (parser.payloadParsedLength() > 0 && parser.payload == 1);
  sender.sendPayload(reset);
  if (reset) hardReset();
}

template<class Messager>
void CoreProtocol<Messager>::handleVersionCommand() {
  if (!(parser.justReceived() && parser.channel[0] == kVersionChannel &&
        parser.channelParsedLength() <= 2)) return;

  if (parser.channelParsedLength() == 1) sendAllVersionMessages();
  else sendVersionMessage(parser.channel[1]);
}

template<class Messager>
void CoreProtocol<Messager>::handleEchoCommand() {
  if (!(parser.justReceived() && parser.channel[0] == kEchoChannel &&
        parser.channelParsedLength() == 1)) return;
  if (parser.payloadParsedLength()) echoValue = parser.payload;

  messager.sendResponse(echoValue);
}

template<class Messager>
void CoreProtocol<Messager>::handleIOCommand() {
  if (!parser.justReceived()) return;
  if (parser.channel[0] != kIOChannel) return;
  if (parser.channelParsedLength() < 3) return;
  if (parser.channelParsedLength() > 4) return;

  // Parse pin number from channels
  if (!isDigit(parser.channel[2])) return;
  uint8_t pin = parser.channel[2] - '0';
  if (parser.channelParsedLength() == 4) {
    pin *= 10;
    if (!isDigit(parser.channel[3])) return;
    pin += parser.channel[3] - '0';
  }

  switch (parser.channel[1]) {
    case kIOAnalogChannel:
      if (pin < kAnalogReadMinPin || pin > kAnalogReadMaxPin) break;
      messager.sendResponse(analogRead(pin + kAnalogPinOffset));
      break;
    case kIODigitalChannel:
      if (pin < kDigitalReadMinPin || pin > kDigitalReadMaxPin) break;
      messager.sendResponse(digitalRead(pin));
      break;
  }
}

template<class Messager>
void CoreProtocol<Messager>::handleBuiltinLEDCommand() {
  if (!(parser.justReceived() && parser.channelParsedLength() > 0 &&
        parser.channel[0] == kBuiltinLEDChannel)) return;

  if (parser.channelParsedLength() == 1) {
    if (parser.payloadParsedLength()) {
      if (parser.payload == 0) led.off();
      else if (parser.payload == 1) led.on();
    }

    sendBuiltinLEDState();

    return;
  }
  handleBuiltinLEDBlinkCommand();
}

template<class Messager>
void CoreProtocol<Messager>::handleBuiltinLEDBlinkCommand() {
  if (!(parser.channelParsedLength() > 1 &&
        parser.channel[1] == kBuiltinLEDBlinkChannel)) return;

  if (parser.channelParsedLength() == 2) {
    if (parser.payloadParsedLength()) {
      if (parser.payload == 1) {
        reportedBlinkEnd = false;
        led.blink();
      } else if (parser.payload == 0) {
        led.off();
      }
    }
    sendBuiltinLEDBlinkState();
    return;
  }

  if (parser.channelParsedLength() > 3) return;
  switch (parser.channel[2]) {
    case kBuiltinLEDBlinkHighIntervalChannel:
      if (parser.payloadParsedLength() && parser.payload > 0) led.highInterval = parser.payload;
      messager.sendResponse(led.highInterval);
      return;
    case kBuiltinLEDBlinkLowIntervalChannel:
      if (parser.payloadParsedLength() && parser.payload > 0) led.lowInterval = parser.payload;
      messager.sendResponse(led.lowInterval);
      return;
    case kBuiltinLEDBlinkPeriodsChannel:
      if (parser.payloadParsedLength()) led.periods = parser.payload;
      sendBuiltinLEDBlinkPeriods();
      return;
    case kBuiltinLEDBlinkNotifyChannel:
      if (parser.payloadParsedLength()) {
        if (parser.payload == 1) reportBlinkUpdates = true;
        else if (parser.payload == 0) reportBlinkUpdates = false;
      }
      messager.sendResponse(reportBlinkUpdates);
      return;
  }
}

template<class Messager>
void CoreProtocol<Messager>::sendBuiltinLEDState() {
    int ledState;
    switch (led.state.current()) {
      case LED::State::on:
      case LED::State::blinkingHigh:
        ledState = 1;
        break;
      case LED::State::off:
      case LED::State::blinkingLow:
        ledState = 0;
        break;
      case LED::State::fadingHigh:
      case LED::State::fadingLow:
        ledState = -1;
        break;
      default:
        return;
    }
    sender.sendChannelStart();
    sender.sendChannelChar(kBuiltinLEDChannel);
    sender.sendChannelEnd();
    sender.sendPayload(ledState);
}

template<class Messager>
void CoreProtocol<Messager>::sendBuiltinLEDBlinkState() {
    bool blink = ((led.state.current() == LED::State::blinkingHigh) ||
        (led.state.current() == LED::State::blinkingLow));
    sender.sendChannelStart();
    sender.sendChannelChar(kBuiltinLEDChannel);
    sender.sendChannelChar(kBuiltinLEDBlinkChannel);
    sender.sendChannelEnd();
    sender.sendPayload(blink);
}

template<class Messager>
void CoreProtocol<Messager>::sendBuiltinLEDBlinkPeriods() {
    sender.sendChannelStart();
    sender.sendChannelChar(kBuiltinLEDChannel);
    sender.sendChannelChar(kBuiltinLEDBlinkChannel);
    sender.sendChannelChar(kBuiltinLEDBlinkPeriodsChannel);
    sender.sendChannelEnd();
    sender.sendPayload(led.periods);
}

}

#endif


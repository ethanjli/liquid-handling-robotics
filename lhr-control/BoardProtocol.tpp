#ifndef BoardProtocol_tpp
#define BoardProtocol_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

// BoardProtocol

template<class Messager>
BoardProtocol<Messager>::BoardProtocol(Messager &messager) :
  led(LED_BUILTIN), messager(messager),
  parser(messager.parser), sender(messager.sender)
{}

template<class Messager>
void BoardProtocol<Messager>::setup() {
  if (setupCompleted) return;

  led.setup();

  setupCompleted = true;
}

template<class Messager>
void BoardProtocol<Messager>::update() {
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
void BoardProtocol<Messager>::onConnect() {
  sendBuiltinLEDState();
}

template<class Messager>
void BoardProtocol<Messager>::handleIOCommand() {
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
void BoardProtocol<Messager>::handleBuiltinLEDCommand() {
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
void BoardProtocol<Messager>::handleBuiltinLEDBlinkCommand() {
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
void BoardProtocol<Messager>::sendBuiltinLEDState() {
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
void BoardProtocol<Messager>::sendBuiltinLEDBlinkState() {
    bool blink = ((led.state.current() == LED::State::blinkingHigh) ||
        (led.state.current() == LED::State::blinkingLow));
    sender.sendChannelStart();
    sender.sendChannelChar(kBuiltinLEDChannel);
    sender.sendChannelChar(kBuiltinLEDBlinkChannel);
    sender.sendChannelEnd();
    sender.sendPayload(blink);
}

template<class Messager>
void BoardProtocol<Messager>::sendBuiltinLEDBlinkPeriods() {
    sender.sendChannelStart();
    sender.sendChannelChar(kBuiltinLEDChannel);
    sender.sendChannelChar(kBuiltinLEDBlinkChannel);
    sender.sendChannelChar(kBuiltinLEDBlinkPeriodsChannel);
    sender.sendChannelEnd();
    sender.sendPayload(led.periods);
}

}

#endif

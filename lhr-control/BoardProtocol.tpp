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
  previousLEDState = led.state.current;
  wdt_reset();
  if (led.state.at(LED::State::off) && led.periods == 0 && !reportedBlinkEnd &&
      (led.state.previouslyAt(LED::State::blinkingHigh) ||
       led.state.previouslyAt(LED::State::blinkingLow))) {
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
  using namespace Channels::BoardProtocol;

  uint8_t channelLength = parser.channelParsedLength;

  if (!parser.justReceived()) return;
  if (parser.channel[0] != kIO) return;
  if (channelLength < 3) return;
  if (channelLength > 4) return;
  // Expects 3 <= channelLength <= 4
  // parsed as: i

  // Parse pin number from channels
  if (!isDigit(parser.channel[2])) return;
  uint8_t pin = parser.channel[2] - '0';
  if (channelLength == 4) {
    pin *= 10;
    if (!isDigit(parser.channel[3])) return;
    pin += parser.channel[3] - '0';
  }

  switch (parser.channel[1]) {
    case IO::kAnalog: // parsed as: ia*
      if (pin < kAnalogReadMinPin || pin > kAnalogReadMaxPin) break;
      messager.sendResponse(analogRead(pin + kAnalogPinOffset));
      break;
    case IO::kDigital: // parsed as: id*
      if (pin < kDigitalReadMinPin || pin > kDigitalReadMaxPin) break;
      messager.sendResponse(digitalRead(pin));
      break;
  }
}

template<class Messager>
void BoardProtocol<Messager>::handleBuiltinLEDCommand() {
  using namespace Channels::BoardProtocol;

  uint8_t channelLength = parser.channelParsedLength;

  if (!(parser.justReceived() && channelLength > 0 &&
        parser.channel[0] == kBuiltinLED)) return;

  // Expects channelLength >= 1
  if (channelLength == 1) { // parsed as: l
    if (parser.receivedPayload()) {
      if (parser.payload == 0) led.off();
      else if (parser.payload == 1) led.on();
    }

    sendBuiltinLEDState();

    return;
  }
  // Expects channelLength >= 2
  handleBuiltinLEDBlinkCommand();
}

template<class Messager>
void BoardProtocol<Messager>::handleBuiltinLEDBlinkCommand() {
  using namespace Channels::BoardProtocol;

  // Expects parser.justReceived()
  uint8_t channelLength = parser.channelParsedLength;

  if (!(channelLength > 1 && parser.channel[1] == BuiltinLED::kBlink)) return;

  // Expects channelLength >= 2
  if (channelLength == 2) { // parsed as: lb
    if (parser.receivedPayload()) {
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

  if (channelLength > 3) return;
  // Expects channelLength == 3
  switch (parser.channel[2]) {
    case BuiltinLED::Blink::kHighInterval: // parsed as: lbh
      if (parser.receivedPayload() && parser.payload > 0) led.highInterval = parser.payload;
      messager.sendResponse(led.highInterval);
      return;
    case BuiltinLED::Blink::kLowInterval: // parsed as: lbl
      if (parser.receivedPayload() && parser.payload > 0) led.lowInterval = parser.payload;
      messager.sendResponse(led.lowInterval);
      return;
    case BuiltinLED::Blink::kPeriods: // parsed as: lbp
      if (parser.receivedPayload()) led.periods = parser.payload;
      sendBuiltinLEDBlinkPeriods();
      return;
    case BuiltinLED::Blink::kNotify: // parsed as: lbn
      if (parser.receivedPayload()) {
        if (parser.payload == 1) reportBlinkUpdates = true;
        else if (parser.payload == 0) reportBlinkUpdates = false;
      }
      messager.sendResponse(reportBlinkUpdates);
      return;
  }
}

template<class Messager>
void BoardProtocol<Messager>::sendBuiltinLEDState() {
  using namespace Channels::BoardProtocol;

  int ledState;
  switch (led.state.current) {
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
  sender.sendChannelChar(kBuiltinLED);
  sender.sendChannelEnd();
  sender.sendPayload(ledState);
}

template<class Messager>
void BoardProtocol<Messager>::sendBuiltinLEDBlinkState() {
  using namespace Channels::BoardProtocol;

  bool blink = led.state.at(LED::State::blinkingHigh) || led.state.at(LED::State::blinkingLow);

  sender.sendChannelStart();
  sender.sendChannelChar(kBuiltinLED);
  sender.sendChannelChar(BuiltinLED::kBlink);
  sender.sendChannelEnd();
  sender.sendPayload(blink);
}

template<class Messager>
void BoardProtocol<Messager>::sendBuiltinLEDBlinkPeriods() {
  using namespace Channels::BoardProtocol;

  sender.sendChannelStart();
  sender.sendChannelChar(kBuiltinLED);
  sender.sendChannelChar(BuiltinLED::kBlink);
  sender.sendChannelChar(BuiltinLED::Blink::kPeriods);
  sender.sendChannelEnd();
  sender.sendPayload(led.periods);
}

}

#endif

